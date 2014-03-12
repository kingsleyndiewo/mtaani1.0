import sys
from cx_Freeze import setup, Executable
sys.setrecursionlimit(10000)
import os

# root path to kivy data
kivy_data_rpath = "../../../../../usr/lib64/python2.7/site-packages/kivy/data/"
kivy_text_rpath = "../../../../../usr/lib64/python2.7/site-packages/kivy/core/"
# make a function to walk over data files and make a list of tuples
def data_lister(data_rpath, target_dir):
    zip_list = []
    root_count = len(data_rpath)
    for root, subfolders, files in os.walk(data_rpath):
        zip_root = root[root_count:]
        for root_file in files:
            zip_list.append((root + '/' + root_file, target_dir + zip_root + '/' + root_file))
    return zip_list

zip_include_list = data_lister(kivy_data_rpath, 'kivy/data/')
zip_include_list.extend(data_lister(kivy_text_rpath, 'kivy/core/'))
# dependencies are automatically detected, but it might need fine tuning.
list_of_excludes = ["tkinter", "werkzeug", "cairo", "cv2", "twisted", "openerp", "Crypto", "gtk-2.0", "scipy",
                    "simplejson", "numpy", "gst-0.10", "xml", "email", "flask", "jinja2", "distutils"]
# options for build        
build_exe_options = {"packages": ["kivy.graphics"], "excludes": list_of_excludes,
    "include_files": ['config//','images//','Ganji//','logs//'],
    "zip_includes" : zip_include_list,
    "icon" : "images/app-icon.ico"
    }

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Ganji 1.0",
        version = "1.0",
        description = "Ganji 1.0 board game",
        options = {"build_exe": build_exe_options},
        executables = [Executable("main.py", base=base)])

# the script is invoked by:
# python setup.py build
# on Windows, an installer can be built by:
# python setup.py bdist_msi