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


"""This module handles translation functions for Wrye Bash."""


"""TODO:
      1) Actually implement the "update from old txt" part of 'Dump'
   """


# Imports ---------------------------------------------------------------------
#-Standard
import locale
import gettext
import sys
import traceback
import subprocess

#-Local
from .Path import GPath


#--Setup locale
if locale.getlocale() == (None, None):
    locale.setlocale(locale.LC_ALL, '')


def Dump(language, outPath, *files):
    """Dumps translatable string from *files to a new txt file in outPath,
       named based on language.  If an already existing translation file exists
       for that language, the new one will be updated with any matching strings
       from the previous one."""
    #--Determine files to dump
    if not files:
        # No files specified.  Assume this file is located in root/src/bolt
        # and we'll dump every .py file in root recursively
        files = []
        mopy = GPath(__file__).realpath.head.head.head
        files = [root.join(file).s for root, dirs, fnames in mopy.walk()
                                   for file_ in fnames
                                   if file_.cext == '.py']
        print('files:')
        for file_ in files:
            print(file_)
    #--Output files
    outTxt = language + 'NEW.txt'
    fullTxt = outPath.join(outTxt)
    tmpTxt = outPath.join(language + 'NEW.tmp')
    oldTxt = outPath.join(language + '.txt')
    #--First dump a fresh translation file
    args = ['p', '-o', fullTxt.s, '-a']
    args.extend(files)
    if hasattr(sys, 'frozen'):
        # Frozen app, the tool scripts aren't accessible
        # Instead, they're included in the package as an
        # importable module
        from . import pygettext
        old_argv = sys.argv[:]
        sys.argv = args
        pygettext.main()
        sys.argv = old_argv
    else:
        p = GPath(sys.prefix).join('Tools', 'i18n', 'pygettext.py')
        args[0] = p.s
        subprocess.call(args, shell=True)
    return outTxt


def Install(language=None, pathRead=None, pathWrite=None):
    """Install translation for language.  If language is not specified,
       installs a translation for the default language."""
    if not language:
        language = locale.getlocale()[0].split('_', 1)[0]
    pathRead = pathRead if pathRead else GPath('l10n')
    pathWrite = pathWrite if pathWrite else pathRead
    if language.lower() == 'german':
        language = 'de'
    txt = pathRead.join(language + '.txt')
    po = pathWrite.join(language + '.po')
    mo = pathWrite.join(language + '.mo')
    #--Test for no translation for the language
    if not txt.exists and not mo.exists:
        if language.lower() != 'english':
            print('No translation file for language:', language)
        trans = gettext.NullTranslations()
    else:
        try:
            # See if translation needs to be recompiled
            if txt.exists:
                txtMtime = txt.mtime
                if not mo.exists or txtMtime != mo.mtime:
                    txt.copy(po)
                    args= ['m', '-o', mo.s, po.s]
                    if hasattr(sys, 'frozen'):
                        # Same thing as for 'Dump' for frozen
                        # apps.
                        from . import msgfmt
                        old_argv = sys.argv[:]
                        sys.argv = args
                        msgfmt.main()
                        sys.argv = old_argv
                    else:
                        m = GPath(sys.prefix).join('Tools', 'i18n', 'msgfmt.py')
                        args[0] = m.s
                        subprocess.call(args, shell=True)
                    po.remove()
                    mo.mtime = txtMtime
            # Create GNU translations
            with mo.open('rb') as ins:
                trans = gettext.GNUTranslations(ins)
        except:
            print('Error loading translation file for', language)
            traceback.print_exc()
            trans = gettext.NullTranslations()
    # Install
    trans.install()
