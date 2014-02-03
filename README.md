Wrye Bash Python 3
==================
Python 3 rewrite and re-factoring of Wrye Bash.  This is very much a work in progress.  Rather than just modifying Wrye Bash's code to run on Python 3, this is a complete rewrite from the ground up.

Requirements:

1. [Python 3.3.x](http://www.python.org/download/releases/3.3.3/ "Python 3.3.3 download page")

   32-bit and 64-bit builds are both acceptable.
2. [wxPython](http://wxpython.org/Phoenix/snapshot-builds/ "wxPython build page")

   Get the latest applicable (32-bit/64-bit) build for Python 3.3.  These are [Python Eggs](http://mrtopf.de/blog/en/a-small-introduction-to-python-eggs/ "An Introduction to Python Eggs"), which are actually kind of a pain to install using Windows if you haven't already setup the required egg packages.  Easiest way to install these is to rename the extension to .zip, extract everything but the EGG-INFO to the Python site-packages directory.

3. [pywin32](https://sourceforge.net/projects/pywin32/files/pywin32/ "pywin32 download page")

   Get the latest applicable build for Python 3.3.  At least version 218 is required.

Also recommended:

* [Python Launcher for Windows](http://blog.python.org/2011/07/python-launcher-for-windows_11.html "Python Launcher for Windows")

  Python 3.3 installs this by default, so no need to download it again.  However, it's worth reading the linked article if you don't know how to put a shebang line into your source files.  Both the Python 2 and Python 3 versions of Wrye Bash have shebang lines, so nothing extra should be needed.
