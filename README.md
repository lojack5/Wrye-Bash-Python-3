Wrye Bash Python 3
==================
Python 3 rewrite and re-factoring of Wrye Bash.  This is very much a work in progress.  Rather than just modifying Wrye Bash's code to run on Python 3, this is a complete rewrite from the ground up.

Requirements:

1. [Python 3.4.x](https://www.python.org/download/releases/3.4.1/ "Python 3.4.1 download page")

   32-bit and 64-bit builds are both acceptable.
2. [wxPython](http://wxpython.org/Phoenix/snapshot-builds/ "wxPython build page")

   Get the latest applicable (32-bit/64-bit) build for Python 3.4, these are denoted by a `cp34` in the file name.  These are [Python Wheel](http://pythonwheels.com/ "Python Wheels") files, which are the new standard to replace Python Eggs.  You can install them using Python's built in tool, `pip.exe`:

   `pip install <path_to_wxPython_whl_file>`

   Or, you can just rename the file to a `.zip` and copy over the `wx` folder to your Python `site-packages` directory.

Also recommended:

* [Python Launcher for Windows](http://blog.python.org/2011/07/python-launcher-for-windows_11.html "Python Launcher for Windows")

  Python 3.3+ installs this by default, so no need to download it again.  However, it's worth reading the linked article if you don't know how to put a shebang line into your source files.  Both the Python 2 and Python 3 versions of Wrye Bash have shebang lines, so nothing extra should be needed.

* [cx_Freeze](http://cx-freeze.sourceforge.net/ "cx_Freeze Sourceforge page") will also be needed to build the Standalone version.  ~~It can be easily installed with `pip.exe`:~~

   ~~`>pip install cx_Freeze`~~
   
   **NOTE:** The current build of cx_Freeze that is installed via `pip` was setup with Python 3.4.0.  For whatever reason, the resulting executables created by cx_Freeze will not execute as a result.  You can get a version that was rebuilt with Python 3.4.1 [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#cx_freeze).  This will supposedly be fixed with a newer version...eventually.

