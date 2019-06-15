# -*- coding: utf-8 -*-
#
#  Copyright (C) 2019 by Igor E. Novikov
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys

import ctypes
from ctypes import wintypes


def fix_sys_argv():
    """Uses shell32.GetCommandLineArgvW to fix sys.argv as a list of
    unicode strings.
    """
    GetCommandLineW = ctypes.cdll.kernel32.GetCommandLineW
    GetCommandLineW.argtypes = []
    GetCommandLineW.restype = wintypes.LPCWSTR
    cmd_line = GetCommandLineW()

    CommandLineToArgvW = ctypes.windll.shell32.CommandLineToArgvW
    CommandLineToArgvW.argtypes = [wintypes.LPCWSTR,
                                   ctypes.POINTER(ctypes.c_int)]
    CommandLineToArgvW.restype = ctypes.POINTER(wintypes.LPWSTR)
    argc = ctypes.c_int(0)
    argv = CommandLineToArgvW(cmd_line, ctypes.byref(argc))

    if argc.value:
        rng = xrange(argc.value - len(sys.argv), argc.value)
        sys.argv = [argv[i] for i in rng]