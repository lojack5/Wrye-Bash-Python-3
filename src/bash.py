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


"""This module does the real working of starting Wrye Bash."""


# Imports ---------------------------------------------------------------------
#--Standard
import os
import sys
import builtins
import traceback
import warnings

#--Local
from . import barg
from . import bass


# Install dummy translation function, so it can be used before translations are
# installed
builtins.__dict__['_'] = lambda x: x


def ErrorMessage(message):
    """Show an error message using GUI if possible."""
    try:
        # Try wx first
        import wx
        from .balt import ShowError
        ShowError(None,message,'Wrye Bash - Error',parseURLs=True)
    except:
        # That failed, try Tkinter
        try:
            import tkinter
            import tkinter.ttk as ttk
            root = tkinter.Tk()
            root.title('Wrye Bash')
            frame = ttk.Frame(root, padding='3 3 3 3')
            frame.pack()
            style = ttk.Style()
            style.configure('TButton')
            button = ttk.Button(text=_('Quit'), command=root.destroy)
            button.pack()#side=tkinter.BOTTOM)
            text = tkinter.Text(frame, wrap='word')
            text.insert(1.0, message)
            text.config(state=tkinter.DISABLED)
            text.pack()
            root.mainloop()
        except:
            # That failed, print to console
            print('Error:', message)


def VerifyRequirements():
    """Check to see if all required dependencies are installed."""
    if hasattr(sys, 'frozen'):
        # Frozen app has the depenancies frozen with it
        return True

    errors = []
    #--wxPython
    try:
        import wx
    except ImportError:
        url = 'http://wiki.wxpython.org/ProjectPhoenix'
        errors.append(
            _('wxPython Phoenix is required.  Get it from:')
            + '\n    <a href="%(url)s">%(url)s</a>' % {'url':url})
    #--Python 3.4
    if sys.version_info[0:2] != (3, 4):
        url = 'https://www.python.org/download/releases/3.4.1/'
        errors.append(
            (_('Python 3.4 is required.  Installed version is %(version)s.'
               '  Get it from:')
             % {'version':'.'.join(map(str, sys.version_info[0:3]))})
            + '\n    <a href="%(url)s">%(url)s</a>' % {'url':url})

    if errors:
        from .balt import VistaDialog
        msg = _('Please ensure the Python dependencies are installed correctly.')
        msg += '\n\n'
        msg += '\n\n'.join(errors)
        VistaDialog(
            None,
            msg,
            _('Wrye Bash'),
            buttons=[(wx.ID_OK, 'Ok')],
            icon='error',
            heading='Cannot start Wrye Bash!')
        return False
    return True


def main():
    # A bug with the current release of wxPhoenix causes wx to try to print to
    # print to warnings.warn, which tries to file.write to stderr, but stderr
    # is None here usually, when launched as a .py file.
    # So instead, we'll tell the warning module to ignore this warning
    # As for the bug: the current build snapshot has wxWidgets at 3.0.2, but
    # but wxPython at 3.0.1, and so it tries to print a warning.
    warnings.filterwarnings(
        'ignore',
        'wxPython/wxWidgets release number mismatch')
    try:
        #--Parse command line
        barg.parse()
        #--Initialize directories
        from . import dirs
        dirs.InitDirs()
        #--Setup translations
        try:
            from .bolt import Translations
            Translations.Install(pathRead=bass.dirs['l10n'],
                                 pathWrite=bass.dirs['l10n.compiled'])
        except Exception as e:
            # Translations fail.  Install a NULL Translations
            # _ function so at least we don't get errors there.
            # TODO: use logging to print
            pass
        #--Check for dependencies
        if not VerifyRequirements():
            return
        #--Start wxApp
        import wx
        app = wx.App()
        #--Test for single instance
        from .bolt import OneInstanceChecker
        if bass.opts.portable:
            oicDir = None # Use defalt
        else:
            oicDir = bass.dirs['appdata'].s
        if not OneInstanceChecker.Start(oicDir):
            return
        del OneInstanceChecker
        #--Run the app!
        #  For now we're just using a dummy frame until we flesh this out
        frame = wx.Frame(None, wx.ID_ANY, _('Haha!'))
        frame.Show()
        if hasattr(sys, 'frozen'):
            frame.SetIcon(wx.Icon(sys.executable, wx.BITMAP_TYPE_ICO))
        else:
            frame.SetIcon(wx.Icon('bash.ico'))
        app.MainLoop()
    except Exception as e:
        #--Something bad happened, try to show it in GUI mode.
        import io
        o = io.StringIO()
        o.write(_('Could not start Wrye Bash:'))
        o.write('\n\n')
        traceback.print_exc(file=o)
        ErrorMessage(o.getvalue())
        raise
