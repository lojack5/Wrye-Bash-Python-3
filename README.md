Wrye Bash Python 3
==================
Python 3 rewrite and re-factoring of Wrye Bash.  This is very much a work in
progress.  Rather than just modifying Wrye Bash's code to run on Python 3,
this is a complete rewrite from the ground up.

Requirements:
1) Python 3.3.x (32-bit or 64-bit version)

     http://www.python.org/download/releases/3.3.3/

2) wxPython Phoenix (grab the latest 3.3 version for 32/64 bit)

     http://wxpython.org/Phoenix/snapshot-builds/

   Latest builds of wxPhoenix are Python EGGs it seems.  These can  either be
   installed using easy install, or my preferred way for something simple like
   this: rename it to a .zip file and extract everything but the EGG-INFO

3) pywin32 (grab latest 32/64-bit version for 3.3)

     https://sourceforge.net/projects/pywin32/files/pywin32/

Also recommended:
1) Python Launcher for Windows is installed by default with Python 3.3, so
   you can continue to maintain a Python 2.x install on your computer.  Just
   make sure to add shebang lines as necessary so your programs use the correct
   Python version.  The Python 2.x Wrye Bash already has the shebang line, as
   does this.

   http://blog.python.org/2011/07/python-launcher-for-windows_11.html
