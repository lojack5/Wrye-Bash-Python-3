# GPL License and Copyright Notice ============================================
#  This file is part of Wrye Bash.
#
#  Wrye Bash is free software; you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  Wrye Bash is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wrye Bash; if not, write to the Free Software Foundation, Inc.,
#  59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Wrye Bash copyright (C) 2005-2009 Wrye
#
# =============================================================================


"""This module contains a class wrapper around path operations, as well as a
   few useful helper functions."""


# Imports ---------------------------------------------------------------------
#--Standard
import os
import stat
import shutil
import time
import random
import sys
import subprocess
import codecs
import tempfile
import binascii
import ctypes
import ctypes.wintypes

#--Local
from src.bolt.Optimize import make_constants, bind_all


# Startupinfo - so subprocess.Popen can launch things with no cmd.exe window
startupinfo = None
if os.name == 'nt':
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW


#--Paths ----------------------------------------------------------------------
Path = None  # Place holder, so GPath doesn't have undefined 'Path'


#--GPaths: global dictionary of saved Path class objects, to avoid duplication
#  when dealing with lots of path items.
_gpaths = {}
def GPath(name):
    """Returns common Path instance for specified name/path."""
    if name is None:
        return None
    elif not name:
        norm = ''
    elif isinstance(name,Path):
        norm = name._s
    elif isinstance(name,str):
        norm = os.path.normpath(name)
    else:
        norm = os.path.normpath(str(name))
    # Lookup
    path = _gpaths.get(norm)
    if path is not None:
        return path
    else:
        return _gpaths.setdefault(norm,Path(norm))


def GPathPurge():
    """Cleans out the _gpaths dictionary of unused Path object."""
    for key in _gpaths.keys():
        if sys.getrefcount(_gpaths[key]) == 2:
            # 1 reference held by _gpaths
            # 1 reference held by this for loop
            del _gpaths[key]


#------------------------------------------------------------------------------
def getcwd():
    """Get the current working directory as a Path object."""
    return GPath(os.getcwd())


def getNorm(name):
    """Return normalized path string for specified string/path object."""
    if not name:
        return name
    elif isinstance(name,Path):
        return name._s
    return os.path.normpath(name)


def getCase(name):
    """Return normalized path + case string for string/path object."""
    if not name:
        return name
    if isinstance(name,Path):
        return name._cs
    return os.path.normcase(os.path.normpath(name))


def tempdir():
    """Returns Path object for the location where temp files are
       created by default for the system."""
    return GPath(tempfile.gettempdir())


def makeTempdir(suffix='', prefix='tmp'):
    """Creates a new temporary directory."""
    return GPath(tempfile.mkdtemp(suffix, prefix))


def _onerror(func, path, exc_info):
    """shutil error handler: remove RO flag"""
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR | stat.S_IWOTH)
        func(path)
    else:
        raise


@make_constants()
class Path(object):
    """A file path.  May be a directory or filename, a full path or relative
       path.  Can include the drive or not.  Supports Pickling."""

    __slots__ = ('_s','_cs','_sroot','_csroot','_shead','_stail','_ext',
                 '_cext', '_sbody','_csbody')

    def __init__(self, name):
        """Initialize."""
        if isinstance(name, Path):
            self.__setstate__(name._s)
        elif isinstance(name, str):
            self.__setstate__(name)
        else:
            raise TypeError('Expected Path or str, got ' + str(type(name)))

    def __getstate__(self):
        """Used by pickler to picked object."""
        return self._s

    def __setstate__(self,norm):
        """Used by unpickler to create object.  Doubles as an initializer."""
        self._s = norm
        self._cs = os.path.normcase(self._s)
        self._sroot, self._ext = os.path.splitext(self._s)
        self._csroot, self._cext = os.path.splitext(self._cs)
        self._shead, self._stail = os.path.split(self._s)
        self._sbody = os.path.basename(self._sroot)
        self._csbody = os.path.basename(self._csroot)

    def __len__(self):
        """Length of path string."""
        return len(self._s)

    def __repr__(self):
        """Representation of Path object."""
        return 'Path('+repr(self._s)+')'

    def __str__(self):
        """Same as self.s, return Path as string"""
        return self._s

    def __add__(self, other):
        """Adds path string/object to self.  Does not insert path
           separators."""
        return GPath(self._s + getNorm(other))

    def __radd__(self, other):
        """Adds self to another path string/object.  Does not insert path
           seperators."""
        return GPath(getNorm(other) + self._s)

    def __truediv__(self, other):
        """Join path to self, including path separator."""
        return GPath(os.path.join(self._s, getNorm(other)))

    def __rtruediv__(self, other):
        """Joins self to another path string/object, including path
           separator."""
        return GPath(os.path.join(getNorm(other), self._s))

    def __hash__(self):
        """Hash function for use as a key for containers."""
        return hash(self._cs)

    #--Comparison functions (__cmp__ doesn't exist in Python 3)
    def __lt__(self, other):
        """Comparison less than."""
        return self._cs < getCase(other)

    def __le__(self, other):
        """Comparison less than or equal to."""
        return self._cs <= getCase(other)

    def __gt__(self, other):
        """Comparison greater than."""
        return self._cs > getCase(other)

    def __ge__(self, other):
        """Comparison greater than or equal to."""
        return self._cs >= getCase(other)

    def __eq__(self, other):
        """Comparison equals function."""
        return self._cs == getCase(other)

    def __ne__(self, other):
        """Comparison not equals function."""
        return self._cs != getCase(other)

    #--Properties ----------------------------------------------------------
    @property
    def s(self):
        """Return path as string."""
        return self._s

    @property
    def cs(self):
        """Return path as case normalized string."""
        return self._cs

    @property
    def sroot(self):
        """Return root as string."""
        return self._sroot

    @property
    def csroot(self):
        """Return root as case normalized string."""
        return self._csroot

    @property
    def shead(self):
        """Return head as string."""
        return self._shead

    @property
    def stail(self):
        """Return tail as string."""
        return self._stail

    @property
    def sbody(self):
        """Return body as string."""
        return self._sbody

    @property
    def csbody(self):
        """Return body as case normalized string."""
        return self._csbody

    @property
    def head(self):
        """For alpha\beta.gamma returns alpha as Path object."""
        return GPath(self._shead)

    @property
    def tail(self):
        """For alpha\beta.gamma returns beta.gamma as Path object."""
        return GPath(self._stail)

    @property
    def body(self):
        """For alpha\beta.gamma returns beta as Path object."""
        return GPath(self._sbody)

    @property
    def root(self):
        """For alpha\beta.gamma returns alpha\beta as Path object"""
        return GPath(self._sroot)

    @property
    def ext(self):
        """Returns extension, including period as string."""
        return self._ext

    @property
    def cext(self):
        """Returns extension, including period, as case normalized string"""
        return self._cext

    @property
    def drive(self):
        """Returns drive as a string."""
        return os.path.splitdrive(self._s)[0]

    @property
    def temp(self,encodingSafe='ascii'):
        """"Returns a temp file path for this file.  If encodingSafe is
            specified, renames the temp path if necessary so it can be
            encoded in the specified encoding.  This would be useful for
            example when used with subprocess.Popen, which encodes to ASCII
            automatically before passing to the command line."""
        path = tempfile.mktemp(prefix='WryeBash_', suffix='.tmp'+self._ext)
        path = Path(path)
        if encodingSafe:
            try:
                path._s.encode(encodingSafe)
            except UnicodeEncodeError:
                path = str(path._s.encode(encodingSafe, 'xmlcharrefreplace'),
                           encodingSafe)
                path = Path(path)
        return path

    @property
    def size(self):
        """Size of file or directory."""
        if os.path.isdir(self._s):
            return sum(sum(map(os.path.getsize,
                               map(lambda z: os.path.join(root,
                                                          dir,
                                                          z),
                                   files)
                                )
                           )
                       for root, dir, files in os.walk(self._s)
                       )
        else:
            return os.path.getsize(self._s)

    @property
    def atime(self):
        """Time file was last accessed."""
        return os.path.getatime(self._s)

    @property
    def ctime(self):
        """Time file was created."""
        return os.path.getctime(self._s)

    #--mtime
    def getmtime(self,maxMTime=False):
        if os.path.isdir(self._s) and maxMTime:
            mtime = max(
                map(os.path.getmtime,
                    itertools.chain(
                        os.path.join(root, x) for x in itertools.chain(dirs,
                                                                        files)
                        for root, dir, files in os.walk(self._s)
                        )
                   )
            )
        else:
            mtime = os.path.getmtime(self._s)
        mtime = int(mtime)
        if mtime <= 0:
            #--Y2038 bug - os.path.getmtime can't handle years past
            #  the Unix epoch, reset to a random time 10 days within
            #  1/1/2037
            mtime = time.mktime((2037, 1, 1, 0, 0, 0, 3, 1, 0))
            mtime += random.randint(10 * 24 * 60 * 60) # 10 days in seconds
            os.utime(self._s, (os.path.getatime(self._s), mtime))
        return mtime

    def setmtime(self,mtime):
        os.utime(self._s, (os.path.getatime(self._s), int(mtime)))

    mtime = property(getmtime, setmtime, doc='Time file was last modified.')

    @property
    def stat(self):
        """File stats from os.stat."""
        return os.stat(self._s)

    @property
    def version(self):
        """File version (exe/dll)."""
        try:
            info = GetFileVersionInfo(self._s)
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            return (_HIWORD(ms), _LOWORD(ms),
                    _HIWORD(ls), _LOWORD(ls))
        except:
            print('error:')
            import traceback
            traceback.print_exc()
            return (0, 0, 0, 0)

    @property
    def version_stripped(self):
        """File version (exe/dll), with leading and trailing zeros removed."""
        version = self.version
        start = 0
        end = 3
        while start < 4:
            if version[start]: break
            start += 1
        else:
            return (0,)
        while end >= 0 and not version[end]:
            end -= 1
        return version[start:end+1]

    @property
    def crc(self):
        """Calculates CRC for self."""
        size = os.path.getsize(self._s)
        crc = 0
        crc32 = binascii.crc32
        with open(self._s, 'rb') as ins:
            insTell = ins.tell
            insRead = ins.read
            while insTell() < size:
                crc = crc32(insRead(2097152), crc) # 2MB at a time
        return crc & 0xFFFFFFFF

    @property
    def exists(self):
        """True if file/directory exists."""
        return os.path.exists(self._s)

    @property
    def isdir(self):
        """True if path exists and is a directory."""
        return os.path.isdir(self._s)

    @property
    def isfile(self):
        """True if path exists and is a file."""
        return os.path.isfile(self._s)

    @property
    def isabs(self):
        """True if path is an absolute path."""
        return os.path.isabs(self._s)

    @property
    def realpath(self):
        """Returns real path (follows symlinks, makes absolute path)"""
        return GPath(os.path.realpath(self._s))

    #--Accessor functions --------------------------------------------------
    def crc_callback(self, callback):
        """Calculates CRC, but allows for a callback for UI feedback.
           callback should be a callable that will be called with how many
           bytes have been read in."""
        size = os.path.getsize(self._s)
        crc = 0
        crc32 = binascii.crc32
        with open(self._s, 'rb') as ins:
            insTell = ins.tell
            insRead = ins.read
            pos = 0
            while pos < size:
                crc = crc32(insRead(2097152), crc) # 2MB at a time
                pos = insTell()
                callback(pos)
        return crc & 0xFFFFFFFF

    def join(*args):
        """Joins self with path elements, using path seperators."""
        return GPath(os.path.join(*map(getNorm, args)))

    def list(self):
        """Returns files/directories in this directory."""
        if not os.path.exists(self._s):
            return []
        return map(GPath, os.listdir(self._s))

    def walk(self, topdown=True, onerror=None, relative=False):
        """Like os.walk"""
        if relative:
            start = len(self._s)
            for root, dirs, files in os.walk(self._s, topdown, onerror):
                yield (GPath(root[start:]),
                       map(GPath,dirs),
                       map(GPath,files))
        else:
            for root, dirs, files in os.walk(self._s, topdown, onerror):
                yield (GPath(root),
                       map(GPath,dirs),
                       map(GPath,files))

    def split(self):
        """Splits the path along path seperators.
           IE: C:\Program Files\Bethesda Softworks
           returns ['C:','Program Files','Bethesda Softworks']"""
        dirs = []
        drive,path = os.path.splitdrive(self._s)
        path = path.rstrip(os.path.sep + os.path.altsep)
        l, r = os.path.split(path)
        while l != '':
            dirs.append(r)
            l, r = os.path.split(l)
        dirs.append(r)
        if drive != '':
            dirs.append(drive)
        dirs.reverse()
        return dirs

    def relpath(self, other):
        """Returns self's relative path to other."""
        return GPath(os.path.relpath(self._s, getNorm(path)))

    def isParent(self, other, followSymlink=False):
        """Return true if this is a parent directory of 'other'."""
        if followSymlink:
            # Easier way, but...
            parent = os.path.normcase(os.path.realpath(self._s))
            child = os.path.normcase(os.path.realpath(getNorm(path)))
        else:
            # ...there are times when we might not want to follow symlinks
            if os.path.isabs(self._s):
                parent = self._cs
            else:
                parent = os.path.join(os.path.normcase(os.getcwd(), self._cs))
            path = getNorm(path)
            if os.path.isabs(path):
                child = os.path.normcase(path)
            else:
                child = os.path.normcase(os.path.join(os.getcwd(), path))

        if not child.startswith(parent):
            return False
        return (os.path.join(parent, child[len(parent):].lstrip(os.path.sep))
                == child)

    def setReadOnly(self, ro):
        """Sets status of read only flag."""
        if ro:
            flag = stat.S_IRUSR | stat.S_IROTH
        else:
            flag = stat.S_IWUSR | stat.S_IWOTH
        if not os.path.isdir(self._s):
            os.chmod(self._s, flag)
        else:
            for root, dirs, files in os.walk(self._s):
                for path in itertools.chain(dirs, files):
                    os.chmod(os.path.join(root, path), flag)

    def getReadOnly(self):
        """Gets status of read only flag."""
        if os.path.exists(self._s):
            if os.path.isfile(self._s):
                try:
                    with open(self._s, 'ab'):
                        return False
                except PermissionError:
                    return True
        return False

    readonly = property(getReadOnly, setReadOnly, doc='Read-only status.')

    def open(self, *args, **kwds):
        """Open file for read/write, etc.  Accepts encoding argument."""
        if self._shead and not os.path.exists(self._shead):
            os.makedirs(self._shead)
        return open(self._s, *args, **kwds)

    def makedirs(self):
        """Create directories"""
        if not os.path.exists(self._s):
            os.makedirs(self._s)

    def remove(self, emptyOnly=False):
        """Smart remove.  Removes a file or directory tree, clearing the
           read-only flag if necessary.  If emptyOnly is True, then if path
           is a directory, only removes empty subdirectories and path if no
           files are present.  No files will be removed in this case.
           For standard Python file/directory remove functions, see:
              removefile, removedir, removedirs, removetree."""
        if os.path.exists(self._s):
            if os.path.isfile(self._s):
                try:
                    os.remove(self._s)
                except PermissionError:
                    os.chmod(self._s, stat.S_IWUSR | stat.S_IWOTH)
                    os.remove(self._s)
            elif emptyOnly:
                # Directory, recursively clean out empty directories
                roCleared = False
                for root, dirs, files in os.walk(self._s):
                    if not files and not dirs:
                        try:
                            os.removedirs(root)
                        except PermissionError:
                            if roCleared:
                                raise
                            self.setReadOnly(False)
                            roCleared = True
                            os.removedirs(root)
                # os.removedirs may have removed parent directories though, so
                # restore those if needed, but keep this directory deleted
                if not os.path.exists(self._s):
                    os.makedirs(self._s)
                    os.removedir(self._s)
            else:
                # Directory, recursively remove everything
                shutil.rmtree(self._s, onerror=_onerror)

    def removefile(self):
        """Removes a file, no error/read-only checking."""
        os.remove(self._s)

    def removedir(self):
        """Removes an empty directory, no error/read-only checking."""
        os.rmdir(self._s)

    def removedirs(self):
        """Removes an empty directory, plus any empty parent directories,
           no error/read-only checking."""
        os.removedirs(self._s)

    def removetree(self):
        """Removes directory and subdirectoris and files recursively."""
        shutil.rmtree(self._s, onerror=_onerror)

    def start(self, exeArgs=None):
        """Starts a file as if doubleclicked in explorer."""
        if self._cext == '.exe':
            if not exeArgs:
                subprocess.Popen([self._s], close_fds=True)
            else:
                subprocess.Popen(exeArgs, executable=self._s, close_fds=True)
        else:
            os.startfile(self._s)

    def copy(self, dest):
        """Copies self to destination."""
        dest = GPath(dest)
        if self._cs == dest._cs:
            return
        if os.path.isdir(self._s):
            shutil.copytree(self._s, dest._s)
        else:
            if dest._shead and not os.path.exists(dest._shead):
                os.makedirs(dest._shead)
            shutil.copyfile(self._s, dest._s)
            os.utime(dest._s, (os.path.getatime(dest._s), self.mtime))

    def move(self, dest):
        """Moves file to destination."""
        dest = GPath(dest)
        if dest._cs == self._cs:
            return
        if dest._shead and not os.path.exists(dest._shead):
            os.makedirs(dest._shead)
        elif os.path.exists(dest._s) and os.path.isfile(self._s):
            os.remove(dest._s)
        try:
            shutil.move(self._s, dest._s)
        except OSError:
            self.readonly = False
            shutil.move(self._s, dest._s)

    def tempMoveTo(self, dest):
        """Temporarily moves file to destination.  Use with the 'with' statement
           After leaving the 'with' statement, file will be moved back."""
        class temp(object):
            __slots__=('_oldpath', '_temppath')
            def __init__(self, oldPath, tempPath):
                self._oldpath = oldPath
                self._temppath = tempPath
            def __enter__(self): return self._temppath
            def __exit__(self, *args, **kwds):
                self._temppath.moveTo(self._oldpath)
        self.moveTo(dest)
        return temp(self, dest)

    def touch(self):
        """Link unix 'touch'.  Creates/updates file with current date/time."""
        if os.path.exists(self._s):
            os.utime(self._s, (os.path.getatime(self._s), time.time()))
        else:
            with open(self._s, 'wb'):
                pass

    def setcwd(self):
        """Set current working directory to self."""
        os.chdir(self._s)


@make_constants()
class PathUnion(object):
    """A Path-like object for directories.  Minimal functions, just useful
       for specifying 2 or more search paths for files.

       MODE_ORDER - when searching for matches for join, the first occurance
           of an existing file is used.  When no match is found, the last
           directory of the union is used.
       MODE_TIMESTAMP - when searching for matches for join, the file with the
           newest timestamp is used.  When no match is found, the last
           directory of the union is uses.
       MODE_REVERSE - Modifies the above, so MODE_ORDER uses the last occurance,
           and no file uses the first directory of the union, MODE_TIMESTAMP
           uses the oldest file."""

    __slots__ = ('dirs','_mode')

    MODE_ORDER = 1
    MODE_REVERSE = 2
    MODE_TIMESTAMP = 4

    def __init__(self, *names, mode=MODE_ORDER):
        self.dirs = [GPath(x) for x in names]
        self._mode = mode
        if mode & PathUnion.MODE_REVERSE:
            self._dirs.reverse()

    def __repr__(self):
        """Representaion of a PathUnion"""
        return 'PathUnion('+str(self.dirs)+')'

    def list(self):
        """Returns list of filenames/dirnames in this union."""
        return set(itertools.chain(*(dirname.list() for dirname in self.dirs)))

    def join(self, *args):
        """Retrun Path object from joining directory with names.  How
           the true path is decided by creation mode."""
        norms = [getNorm(x) for x in args]
        if self._mode & PathUnion.MODE_TIMESTAMP:
            # Newest/oldest file returned
            if self._mode & PathUnion.MODE_REVERSE:
                def getmatch(old, new):
                    if not old:
                        return new
                    if os.path.getmtime(old) < os.path.getmtime(new):
                        return old
                    return new
            else:
                def getmatch(old, new):
                    if not old:
                        return new
                    if os.path.getmtime(old) < os.path.getmtime(new):
                        return new
                    return old
            match = None
            for dirname in self.dirs:
                full = os.path.join(dirname._s, *norms)
                if os.path.exists(full):
                    match = getmatch(match,full)
            if match:
                return GPath(match)
        else: # MODE_ORDER
            # First/last match returned
            for dirname in self.dirs:
                full = os.path.join(dirname._s, *norms)
                if os.path.exists(full):
                    return GPath(full)
        # None exist, use first directory to create
        return self.dirs[0].join(*norms)


# Win32API --------------------------------------------------------------------
# Various win32api stuff that Path needs: GetFileVersionInfo,
# and SHGetFolderPath
def _HIWORD(dw):
    return (dw & 0xFFFF0000) >> 16


def _LOWORD(dw):
    return dw & 0x0000FFFF


def GetFileVersionInfo(fileName):
    # Optimize doesn't like when the next 3 declarations are in the global
    # global scope, ends up in an infinite recursive optimization loop
    from ctypes.wintypes import DWORD
    class FFI(ctypes.Structure):
        # VS_FIXEDFILEINFO
        _fields_ = [
            ('Signature', DWORD),
            ('StrucVersion', DWORD),
            ('FileVersionMS', DWORD),
            ('FileVersionLS', DWORD),
            ('ProductVersionMS', DWORD),
            ('ProductVersionLS', DWORD),
            ('FileFlagMask', DWORD),
            ('FileFlags', DWORD),
            ('FileOS', DWORD),
            ('FileType', DWORD),
            ('FileSubtype', DWORD),
            ('FileDateMS', DWORD),
            ('FileDateLS', DWORD),
            ]
    P_FFI = ctypes.POINTER(FFI)
    size = ctypes.windll.version.GetFileVersionInfoSizeW(fileName, None)
    if not size:
        return None
    res = ctypes.create_string_buffer(size)
    ctypes.windll.version.GetFileVersionInfoW(fileName, None, size, res)
    r = P_FFI()
    l = ctypes.c_uint()
    ctypes.windll.version.VerQueryValueW(res, '\\', ctypes.byref(r), ctypes.byref(l))
    if not l.value:
        return None
    r = r.contents
    return {x[0]:getattr(r,x[0]) for x in FFI._fields_}

    
_csidls = {
    # Only reproduce a few of the shell folders here, even most of these won't
    # be used.
    'DESKTOP': 0,
    'PROGRAMS': 2,
    'PERSONAL': 5,
    'FAVORITES': 6,
    'STARTUP': 7,
    'RECENT': 8,
    'SENDTO': 9,
    'STARTMENU': 11,
    'APPDATA': 26,
    'LOCAL_APPDATA': 28,
    }


def _shell_path(name):
    SHGetFolderPath = ctypes.windll.shell32.SHGetFolderPathW
    SHGetFolderPath.argtypes = [ctypes.wintypes.HWND,
                                ctypes.c_int,
                                ctypes.wintypes.HANDLE,
                                ctypes.wintypes.DWORD,
                                ctypes.wintypes.LPCWSTR]
    path_buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    error = SHGetFolderPath(0, _csidls.get(name), 0, 0, path_buf)
    return GPath(path_buf.value)


Desktop = _shell_path('DESKTOP')
AppData = _shell_path('APPDATA')
LocalAppData = _shell_path('LOCAL_APPDATA')
Favorites = _shell_path('FAVORITES')
StartMenu = _shell_path('STARTMENU')
Programs = _shell_path('PROGRAMS')
Startup = _shell_path('STARTUP')
Personal = _shell_path('PERSONAL')
Recent = _shell_path('RECENT')
SendTo = _shell_path('SENDTO')


# Clean up a little
del _shell_path
del _csidls


bind_all(globals(), stoplist=['_gpaths'])
