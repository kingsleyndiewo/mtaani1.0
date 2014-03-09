import sys
from cx_Freeze import setup, Executable
sys.setrecursionlimit(10000)

# Dependencies are automatically detected, but it might need fine tuning.
list_of_excludes = ["tkinter", "werkzeug", "cairo", "cv2", "twisted", "openerp", "Crypto", "gtk-2.0", "scipy",
                    "simplejson", "numpy", "gst-0.10", "xml", "email", "flask", "jinja2", "json", "distutils"]
build_exe_options = {"packages": ["os"], "excludes": list_of_excludes,
    "include_files": ['config//','images//','Ganji//'],
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