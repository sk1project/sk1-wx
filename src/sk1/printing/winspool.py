# -*- coding: utf-8 -*-
#
#  Winspoll connector
#
#  Copyright (C) 2016 by Ihor E. Novikov
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

import ctypes
from ctypes.wintypes import BYTE, DWORD, LPCWSTR
from ctypes import c_long, c_ulong, byref, c_short, c_int, c_char
from ctypes import POINTER, create_unicode_buffer

winspool = ctypes.WinDLL('winspool.drv')
msvcrt = ctypes.cdll.msvcrt

PRINTER_ENUM_LOCAL = 2
NAME = None

PSECURITY_DESCRIPTOR = POINTER(BYTE)


class PRINTER_INFO_1(ctypes.Structure):
    _fields_ = [
        ("Flags", DWORD),
        ("pDescription", LPCWSTR),
        ("pName", LPCWSTR),
        ("pComment", LPCWSTR),
    ]


class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", c_char * 32),
        ("dmSpecVersion", c_short),
        ("dmDriverVersion", c_short),
        ("dmSize", c_short),
        ("dmDriverExtra", c_short),
        ("dmFields", c_int),

        ("dmOrientation", c_short),
        ("dmPaperSize", c_short),
        ("dmPaperLength", c_short),
        ("dmPaperWidth", c_short),
        ("dmScale", c_short),
        ("dmCopies", c_short),
        ("dmDefaultSource", c_short),
        ("dmPrintQuality", c_short),

        ("dmColor", c_short),
        ("dmDuplex", c_short),
        ("dmYResolution", c_short),
        ("dmTTOption", c_short),
        ("dmCollate", c_short),
        ("dmFormName", c_char * 32),
        ("dmLogPixels", c_int),
        ("dmBitsPerPel", c_long),
        ("dmPelsWidth", c_long),
        ("dmPelsHeight", c_long),
        ("dmDisplayFlags", c_long),
        ("dmDisplayFrequency", c_long)
    ]


class PRINTER_INFO_2(ctypes.Structure):
    _fields_ = [
        ("pServerName", LPCWSTR),
        ("pPrinterName", LPCWSTR),
        ("pShareName", LPCWSTR),
        ("pPortName", LPCWSTR),
        ("pDriverName", LPCWSTR),
        ("pComment", LPCWSTR),
        ("pLocation", LPCWSTR),
        ("pDevMode", POINTER(DEVMODE)),
        ("pSepFile", LPCWSTR),
        ("pPrintProcessor", LPCWSTR),
        ("pDatatype", LPCWSTR),
        ("pParameters", LPCWSTR),
        ("pSecurityDescriptor", POINTER(BYTE)),
        ("Attributes", DWORD),
        ("Priority", DWORD),
        ("DefaultPriority", DWORD),
        ("StartTime", DWORD),
        ("UntilTime", DWORD),
        ("Status", DWORD),
        ("cJobs", DWORD),
        ("AveragePPM", DWORD),
    ]


def get_printer_names():
    names = []
    info = ctypes.POINTER(BYTE)()
    pcbNeeded = DWORD(0)
    pcReturned = DWORD(0)
    winspool.EnumPrintersW(PRINTER_ENUM_LOCAL, NAME, 1, ctypes.byref(info),
                           0, ctypes.byref(pcbNeeded), ctypes.byref(pcReturned))
    bufsize = pcbNeeded.value
    if bufsize:
        buff = msvcrt.malloc(bufsize)
        winspool.EnumPrintersW(PRINTER_ENUM_LOCAL, NAME, 1, buff, bufsize,
                               ctypes.byref(pcbNeeded),
                               ctypes.byref(pcReturned))
        info = ctypes.cast(buff, ctypes.POINTER(PRINTER_INFO_1))
        for i in range(pcReturned.value):
            names.append(info[i].pName)
        msvcrt.free(buff)
    return names


def get_default_printer():
    plen = DWORD(0)
    winspool.GetDefaultPrinterW(None, byref(plen))
    pname = create_unicode_buffer(plen.value)
    winspool.GetDefaultPrinterW(pname, byref(plen))
    return pname.value


def open_printer(prtname):
    if not prtname:
        prtname = get_default_printer()
    hptr = c_ulong()
    if winspool.OpenPrinterW(prtname, byref(hptr), None): return hptr
    return None


def close_printer(handle):
    if handle:
        winspool.ClosePrinter(handle)


def is_color_printer(prtname):
    ret = False
    if not prtname:
        prtname = get_default_printer()
    hptr = open_printer(prtname)
    info = ctypes.POINTER(BYTE)()
    cbBuf = DWORD(0)
    pcbNeeded = DWORD(0)
    winspool.GetPrinterA(hptr, 2, ctypes.byref(info),
                         cbBuf, ctypes.byref(pcbNeeded))
    bufsize = pcbNeeded.value
    if bufsize:
        buff = msvcrt.malloc(bufsize)
        winspool.GetPrinterA(hptr, 2, buff, bufsize, ctypes.byref(pcbNeeded))
        info = ctypes.cast(buff, ctypes.POINTER(PRINTER_INFO_2))
        ret = info.contents.pDevMode.contents.dmColor == 2
        msvcrt.free(buff)
    close_printer(hptr)
    return ret
