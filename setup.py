#!/usr/bin/env python3.4
#
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

"""This is the py2exe distutils script for building the Wrye Bash standalone
   executable."""

# Imports ---------------------------------------------------------------------
#--Standard
from distutils.core import setup
import os
import shutil
import sys
import platform

#-- 3rd party
import py2exe

#-- Local
import src.bass


# Utility functions
def remove(path):
    '''Remove a file/directory if it exists'''
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)

def move(src, dest):
    '''move a file if it exists'''
    if os.path.exists(src):
        shutil.move(src, dest)


class Target:
    '''File info for an exe'''
    def __init__(self):
        self.name = 'Wrye Bash'
        self.product_name = self.name
        self.description = 'The Elder Scrolls modding Swiss Army Knife.'
        self.version = src.bass.version
        self.author = 'Wrye Bash Team'
        self.copyright = '2014'
        self.url = 'https://github.com/lojack5/Wrye-Bash-Python-3'
        self.download_url = self.url
        self.script = 'Wrye Bash.pyw'
        self.icon_resources = [(1, 'bash.ico')]


print('Cleaning output directory.')
try:
    remove('dist')
except:
    print('Could not clean output directory, a file may be in use.')
    sys.exit(1)

# Copy translation tools to this dir so they can get included
msgfmt = os.path.join(sys.prefix, 'Tools', 'i18n', 'msgfmt.py')
pygettext = os.path.join(sys.prefix, 'Tools', 'i18n', 'pygettext.py')
msgfmtTo = os.path.join('src', 'bolt', 'msgfmt.py')
pygettextTo = os.path.join('src', 'bolt', 'pygettext.py')


# Additional external files needed by Bash
if '64bit' in platform.architecture():
    xtask = 'bin\\XTaskDlg32.dll'
else:
    xtask = 'bin\\XTaskDlg64.dll'

extras = [
    ('l10n', ['l10n\\english.txt',
              ]),
    ('bin', [xtask,
             ]),
    ]


def main():
    print('Copying translation scripts.')
    shutil.copy(msgfmt, msgfmtTo)
    shutil.copy(pygettext, pygettextTo)
    # Build
    setup(
        windows = [Target()],
        options = {
            'py2exe': {
                'dll_excludes': [
                    ],
                'includes': [
                    ],
                'excludes': [
                    # Things to NOT exclude:
                    # 'socket',  # Needed by msgfmt
                    # '_socket', # Needed by msgfmt

                    # The following are suggested in the py2exe tutorial
                    # they are generally imports that are never actually used
                    '_ssl',
                    'ssl',
                    'pdb',
                    'unittest',
                    'distutils',
                    'doctest',
                    'difflib',
                    # tkinter not needed since wx will be guaranteed to be included
                    'tkinter',
                    # fintl is referenced by pygettest as a self test, not needed
                    'fintl',
                    # Carbon is used by wx.lib.colourutils - which is not used
                    'Carbon',
                    # Others that just simply aren't used
                    'optparse',
                    ],
                'ignores': [],
                'bundle_files': 0,  # 0 = everything
                'optimize': 2,      # 2 = full optimization
                'compressed': True,
                },
            },
        data_files = extras,
        zipfile = 'bin/library.dat', # Put bundled files in an along side file
        )


    print('Cleaning up translation scripts.')
    remove(msgfmtTo)
    remove(pygettextTo)

if __name__=='__main__':
    if sys.argv[-1].lower() != 'py2exe':
        sys.argv.append('py2exe')
    main()
