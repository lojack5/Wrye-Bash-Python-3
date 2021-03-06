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


"""This module contains UI elements specific to Windows Vista and later.

   The TaskDialog code is from taskdialog.py, license below:

       taskdialog.py

       Copyright © 2009 Te-jé Rodgers <contact@tejerodgers.com>

       This file is part of Curtains

       Curtains is free software; you can redistribute it and/or modify
       it under the terms of the GNU Lesser General Public License as
       published by the Free Software Foundation; either version 3 of the
       License, or (at your option) any later version.

       This program is distributed in the hope that it will be useful,
       but WITHOUT ANY WARRANTY; without even the implied warranty of
       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
       GNU Lesser General Public License for more details.

       You should have received a copy of the GNU Lesser General Public License
       along with this program; if not, write to the Free Software
       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
       MA 02110-1301, USA.
   """


# Imports ---------------------------------------------------------------------
from ctypes import *
import ctypes.wintypes as wintypes
import winreg
import subprocess
import platform
import os


#==SetUAC =====================================================================
#==============================================================================
_SendMessage = windll.user32.SendMessageW
_SendMessage.argtypes = [wintypes.HWND,
                         c_uint,
                         wintypes.WPARAM,
                         wintypes.LPARAM]

def SetUAC(handle, uac=True):
    """Sets a button to a UAC button (shield icon)"""
    _SendMessage(handle, 0x160C, None, uac)


def StartURL(url):
    """Opens URL in default browser.  Do it this way instead of os.startfile or
       ShellExecute, because anchors get lost using those."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,
                             'http\\shell\\open\\command')
        value = winreg.EnumValue(key, 0)
        cmd = value[1]
        cmd = cmd.replace('%1', url)
        subprocess.Popen(cmd)
    except WindowsError:
        # Regestry failed, fallback to Python standard method
        import webbrowser
        webbrowser.open(url, new=2)


def StartURLCallback(dialog, url):
    StartURL(url)


#==TaskDialog =================================================================
#==============================================================================
BUTTONID_OFFSET                 = 1000


#---Internal Flags. Leave these alone unless you know what you're doing---#
ENABLE_HYPERLINKS               = 0x0001
USE_HICON_MAIN                  = 0x0002
USE_HICON_FOOTER                = 0x0004
ALLOW_DIALOG_CANCELLATION       = 0x0008
USE_COMMAND_LINKS               = 0x0010
USE_COMMAND_LINKS_NO_ICON       = 0x0020
EXPAND_FOOTER_AREA              = 0x0040
EXPANDED_BY_DEFAULT             = 0x0080
VERIFICATION_FLAG_CHECKED       = 0x0100
SHOW_PROGRESS_BAR               = 0x0200
SHOW_MARQUEE_PROGRESS_BAR       = 0x0400
CALLBACK_TIMER                  = 0x0800
POSITION_RELATIVE_TO_WINDOW     = 0x1000
RTL_LAYOUT                      = 0x2000
NO_DEFAULT_RADIO_BUTTON         = 0x4000
CAN_BE_MINIMIZED                = 0x8000


#-------------Events---------------#
CREATED                         = 0
NAVIGATED                       = 1
BUTTON_CLICKED                  = 2
HYPERLINK_CLICKED               = 3
TIMER                           = 4
DESTROYED                       = 5
RADIO_BUTTON_CLICKED            = 6
DIALOG_CONSTRUCTED              = 7
VERIFICATION_CLICKED            = 8
HELP                            = 9
EXPANDER_BUTTON_CLICKED         = 10


#-------Callback Type--------#
PFTASKDIALOGCALLBACK = WINFUNCTYPE(c_void_p, c_void_p, c_uint, c_uint,
                                   c_long, c_long)


#-------Win32 Stucts/Unions--------#
# Callers do not have to worry about using these.
class TASKDIALOG_BUTTON(Structure):
    _fields_ = [('nButtonID', c_int),
                ('pszButtonText', c_wchar_p)]


class FOOTERICON(Union):
    _fields_ = [('hFooterIcon', c_void_p),
                ('pszFooterIcon', c_ushort)]


class MAINICON(Union):
    _fields_ = [('hMainIcon', c_void_p),
                ('pszMainIcon', c_ushort)]


class TASKDIALOGCONFIG(Structure):
    _pack_ = 1
    _anonymous_ = ("uMainIcon", "uFooterIcon",)
    _fields_ = [('cbSize', c_uint),
                ('hwndParent', c_void_p),
                ('hInstance', c_void_p),
                ('dwFlags', c_uint),
                ('dwCommonButtons', c_uint),
                ('pszWindowTitle', c_wchar_p),
                ('uMainIcon', MAINICON),
                ('pszMainInstruction', c_wchar_p),
                ('pszContent', c_wchar_p),
                ('cButtons', c_uint),
                ('pButtons', POINTER(TASKDIALOG_BUTTON)),
                ('nDefaultButton', c_int),
                ('cRadioButtons', c_uint),
                ('pRadioButtons', POINTER(TASKDIALOG_BUTTON)),
                ('nDefaultRadioButton', c_int),
                ('pszVerificationText', c_wchar_p),
                ('pszExpandedInformation', c_wchar_p),
                ('pszExpandedControlText', c_wchar_p),
                ('pszCollapsedControlText', c_wchar_p),
                ('uFooterIcon', FOOTERICON),
                ('pszFooter', c_wchar_p),
                ('pfCallback', PFTASKDIALOGCALLBACK),
                ('lpCallbackData', c_long),
                ('cxWidth', c_uint),
                ]


try:
    if '64bit' in platform.architecture():
        name = 'XTaskDlg64.dll'
    else:
        name = 'XTaskDlg32.dll'
    xtaskdlg = WinDLL(os.path.join('bin',name))
    indirect = xtaskdlg.TaskDialogIndirect
    indirect.restype = c_void_p
    Available = True
except AttributeError:
    Available = False


#------Message codes------#
_SETISMARQUEE = 1127
_SETPBARRANGE = 1129
_SETPBARPOS = 1130
_SETMARQUEE = 1131
_SETELEMENT = 1132
_SETSHIELD = 1139
_UPDATEICON = 1140


_CONTENT = 0
_EX_INFO = 1
_FOOTER = 2
_HEADING = 3


class TaskDialog(object):
    """Wrapper class for the Win32 task dialog."""

    stock_icons = {'warning': 65535,
                   'error': 65534,
                   'information': 65533,
                   'shield': 65532}

    stock_buttons = {'ok': 0x01,
                     'yes': 0x02,
                     'no': 0x04,
                     'cancel': 0x08,
                     'retry': 0x10,
                     'close': 0x20}

    stock_button_ids = {'ok': 1,
                        'cancel': 2,
                        'retry': 4,
                        'yes': 6,
                        'no': 7,
                        'close': 8}

    def __init__(self, title, heading, content, buttons=[], icon=None,
                 parenthwnd=None):
        """Initialize the dialog."""
        self.__events = {CREATED: [],
                         NAVIGATED: [],
                         BUTTON_CLICKED: [],
                         HYPERLINK_CLICKED: [],
                         TIMER: [],
                         DESTROYED: [],
                         RADIO_BUTTON_CLICKED: [],
                         DIALOG_CONSTRUCTED: [],
                         VERIFICATION_CLICKED: [],
                         HELP: [],
                         EXPANDER_BUTTON_CLICKED: []}
        self.__stockb_indices = []
        self.__shield_buttons = []
        self.__handle = None

        self.set_title(title)
        self.set_heading(heading)
        self.set_content(content)
        self.set_buttons(buttons)
        self.set_main_icon(icon)
        self._set_parent_hwnd(parenthwnd)

    def close(self):
        """Close the task dialog."""
        windll.user32.SendMessageW(self.__handle, 0x0010, 0, 0)

    def bind(self, event, func):
        """Bind a function to one of the task dialog events."""
        if event not in self.__events.keys():
            raise Exception("The control does not support the event.")
        self.__events[event].append(func)
        return self

    def set_title(self, title):
        """Set the window title of the dialog. Calling this has not effect after
           show has been called."""
        self._title = title
        return self

    def set_heading(self, heading):
        """Set the heading / main instruction of the dialog."""
        self._heading = heading
        if self.__handle != None:
            self.__update_element_text(_HEADING, heading)
        return self

    def set_content(self, content):
        """Set the text content or message that the dialog conveys."""
        self._content = content
        if self.__handle != None:
            self.__update_element_text(_CONTENT, content)
        return self

    def set_footer(self, footer):
        """Set the footer text of the dialog."""
        self._footer = footer
        if self.__handle != None:
            self.__update_element_text(_FOOTER, footer)
        return self

    def set_buttons(self, buttons, convert_stock_buttons=True):
        """Set the buttons on the dialog using the list of strings in *buttons*
           where each string is the label for a new button.

           See the official documentation.
        """
        self._buttons = buttons
        self._conv_stock = convert_stock_buttons
        return self

    def set_radio_buttons(self, buttons, default=0):
        """Add radio buttons to the dialog using the list of strings in
           *buttons*.
        """
        self._radio_buttons = buttons
        self._default_radio = default
        return self

    def set_main_icon(self, icon):
        """Set the icon that appears at the top of the dialog."""
        if icon == None: return self
        if icon in self.stock_icons.keys():
            self._main_icon = self.stock_icons[icon]
            self._main_is_stock = True
        else:
            self._main_icon = icon
            self._main_is_stock = False
        return self

    def set_footer_icon(self, icon):
        """Set the icon that appears in the footer of the dialog."""
        if icon in self.stock_icons.keys():
            self._footer_icon = self.stock_icons[icon]
            self._footer_is_stock = True
        else:
            self._footer_icon = icon
            self._footer_is_stock = False
        return self

    def set_expander(self, expander_data, expanded=False, at_footer=False):
        """Set up a collapsible control that can reveal further information
           about the task that the dialog performs."""
        if len(expander_data) != 3: return self
        self._expander_data = expander_data
        self._expander_expanded = expanded
        self._expands_at_footer = at_footer
        return self

    def set_rangeless_progress_bar(self, ticks=50):
        """Set the progress bar on the task dialog as a marquee progress bar."""
        self._marquee_progress_bar = True
        self._marquee_speed = ticks
        return self

    def set_progress_bar(self, callback, low=0, high=100, pos=0):
        """Set the progress bar on the task dialog as a marquee progress bar."""
        _range = (high << 16) | low
        self._progress_bar = {'func': callback, 'range': _range, 'pos': pos}
        return self


    def set_check_box(self, label, checked=False):
        """Set up a verification check box that appears on the task dialog."""
        self._cbox_label = label
        self._cbox_checked = checked
        return self

    def set_width(self, width):
        """Set the width, in pixels, of the taskdialog."""
        self._width = width
        return self

    def _set_parent_hwnd(self, hwnd):
        self._parent = hwnd

    def show(self, command_links=False, centered=True, can_cancel=False,
             can_minimize=False, hyperlinks=True, additional_flags=0):
        """Build and display the dialog box."""
        conf = self.__configure(command_links, centered, can_cancel,
                                can_minimize, hyperlinks, additional_flags)
        button = c_int()
        radio = c_int()
        checkbox = c_int()
        indirect(byref(conf), byref(button), byref(radio), byref(checkbox))

        if button.value >= BUTTONID_OFFSET:
            button = self.__custom_buttons[button.value - BUTTONID_OFFSET][0]
        else:
            for key, value in self.stock_button_ids.items():
                if value == button.value:
                    button = key
                    break
            else:
                button = 0

        if getattr(self, '_radio_buttons', False):
            radio = self._radio_buttons[radio.value]
        else:
            radio = radio.value

        if checkbox.value == 0:
            checkbox = False
        else:
            checkbox = True

        return (button, radio, checkbox)

    def __configure(self, c_links, centered, close, minimize, h_links, flags):
        conf = TASKDIALOGCONFIG()

        if c_links and len(getattr(self, '_buttons', [])) > 0:
            flags = flags | USE_COMMAND_LINKS
        if centered:
            flags = flags | POSITION_RELATIVE_TO_WINDOW
        if close:
            flags = flags | ALLOW_DIALOG_CANCELLATION
        if minimize:
            flags = flags | CAN_BE_MINIMIZED
        if h_links:
            flags = flags | ENABLE_HYPERLINKS

        conf.cbSize = sizeof(TASKDIALOGCONFIG)
        conf.hwndParent = self._parent
        conf.pszWindowTitle = self._title
        conf.pszMainInstruction = self._heading
        conf.pszContent = self._content

        attrs = dir(self)

        if '_width' in attrs:
            conf.cxWidth = self._width

        if '_footer' in attrs:
            conf.pszFooter = self._footer
        if '_footer_icon' in attrs:
            if self._footer_is_stock:
                conf.uFooterIcon.pszFooterIcon = self._footer_icon
            else:
                conf.uFooterIcon.hFooterIcon = self._footer_icon
                flags = flags | USE_HICON_FOOTER
        if '_main_icon' in attrs:
            if self._main_is_stock:
                conf.uMainIcon.pszMainIcon = self._main_icon
            else:
                conf.uMainIcon.hMainIcon = self._main_icon
                flags = flags | USE_HICON_MAIN

        if '_buttons' in attrs:
            custom_buttons = []
            # Enumerate through button list
            for i, button in enumerate(self._buttons):
                text, elevated, default = self.__parse_button(button)

                if (text.lower() in self.stock_buttons.keys()
                    and self._conv_stock):
                    # This is a stock button.
                    conf.dwCommonButtons = (conf.dwCommonButtons
                                            |self.stock_buttons[text.lower()])

                    bID = self.stock_button_ids[text.lower()]
                    if elevated:
                        self.__shield_buttons.append(bID)
                    if default:
                        conf.nDefaultButton = bID
                else:
                    custom_buttons.append((text, default, elevated))

            conf.cButtons = len(custom_buttons)
            array_type = ARRAY(TASKDIALOG_BUTTON, conf.cButtons)
            c_array = array_type()
            for i, tup in enumerate(custom_buttons):
                c_array[i] = TASKDIALOG_BUTTON(i + BUTTONID_OFFSET, tup[0])
                if tup[1]:
                    conf.nDefaultButton = i + BUTTONID_OFFSET
                if tup[2]:
                    self.__shield_buttons.append(i + BUTTONID_OFFSET)
            conf.pButtons = c_array
            self.__custom_buttons = custom_buttons

        if '_radio_buttons' in attrs:
            conf.cRadioButtons = len(self._radio_buttons)
            array_type = ARRAY(TASKDIALOG_BUTTON, conf.cRadioButtons)
            c_array = array_type()
            for i, button in enumerate(self._radio_buttons):
                c_array[i] = TASKDIALOG_BUTTON(i, button)
            conf.pRadioButtons = c_array

            if self._default_radio == None:
                flags = flags | NO_DEFAULT_RADIO_BUTTON
            else:
                conf.nDefaultRadioButton = self._default_radio

        if '_expander_data' in attrs:
            conf.pszCollapsedControlText = self._expander_data[0]
            conf.pszExpandedControlText = self._expander_data[1]
            conf.pszExpandedInformation = self._expander_data[2]

            if self._expander_expanded:
                flags = flags | EXPANDED_BY_DEFAULT
            if self._expands_at_footer:
                flags = flags | EXPAND_FOOTER_AREA

        if '_cbox_label' in attrs:
            conf.pszVerificationText = self._cbox_label
            if self._cbox_checked:
                flags = flags | VERIFICATION_FLAG_CHECKED

        if '_marquee_progress_bar' in attrs:
            flags = flags | SHOW_MARQUEE_PROGRESS_BAR
            flags = flags | CALLBACK_TIMER

        if '_progress_bar' in attrs:
            flags = flags | SHOW_PROGRESS_BAR
            flags = flags | CALLBACK_TIMER

        conf.dwFlags = flags
        conf.pfCallback = PFTASKDIALOGCALLBACK(self.__callback)
        return conf

    def __parse_button(self, text):
        elevation = False
        default = False

        if text.startswith('+') and len(text) > 1:
            text = text[1:]
            elevation = True
        elif text.startswith(r'\+'):
            text = text[1:]

        if text.startswith('+\\') and text.isupper():
            text = text[0] + text[2:]
        elif text.startswith('\\') and text.isupper():
            text = text[1:]
        elif text.isupper():
            default = True
            splits = text.partition('&')
            if splits[0] == '':
                text = splits[1] + splits[2].capitalize()
            else:
                text = splits[0].capitalize() + splits[1] + splits[2]

        return text, elevation, default

    def __callback(self, handle, notification, wparam, lparam, refdata):
        args = [self]
        if notification == CREATED:
            self.__handle = handle

            for bID in self.__shield_buttons:
                windll.user32.SendMessageW(self.__handle, _SETSHIELD, bID, 1)

            if getattr(self, '_marquee_progress_bar', False):
                self.__set_marquee_speed()

        elif notification == BUTTON_CLICKED:
            if wparam >= BUTTONID_OFFSET:
                button = self.__custom_buttons[wparam - BUTTONID_OFFSET][0]
                args.append(button)
            else:
                for key, value in self.stock_button_ids.items():
                    if value == wparam:
                        button = key
                        break
                else:
                    button = 0
                args.append(button)

        elif notification == HYPERLINK_CLICKED:
            args.append(wstring_at(lparam))

        elif notification == RADIO_BUTTON_CLICKED:
            if getattr(self, '_radio_buttons', False):
                radio = self._radio_buttons[wparam]
            else:
                radio = wparam
            args.append(radio)

        elif notification == VERIFICATION_CLICKED:
            args.append(wparam)

        elif notification == EXPANDER_BUTTON_CLICKED:
            if wparam == 0:
                collapsed = True
            else:
                collapsed = False
            args.append(collapsed)

        elif notification == DESTROYED:
            self.__handle = None

        elif notification == TIMER:
            args.append(wparam)

            if getattr(self, '_progress_bar', False):
                callback = self._progress_bar['func']
                new_pos = callback(self)
                self._progress_bar['pos'] = new_pos
                self.__update_progress_bar()

        for func in self.__events[notification]:
            func(*args)

    def __set_marquee_speed(self):
        windll.user32.SendMessageW(self.__handle, _SETMARQUEE,
                                   1, self._marquee_speed)

    def __update_element_text(self, element, text):
        if self.__handle == None:
            raise Exception("Dialog is not yet created, or has been destroyed.")
        windll.user32.SendMessageW(self.__handle, _SETELEMENT, element, text)

    def __update_progress_bar(self):
        windll.user32.SendMessageW(self.__handle, _SETPBARRANGE, 0,
                                   self._progress_bar['range'])
        windll.user32.SendMessageW(self.__handle, _SETPBARPOS,
                                   self._progress_bar['pos'], 0)
