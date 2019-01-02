# -*- coding: utf-8 -*-
#
#  Copyright (C) 2003-2011 by Igor E. Novikov
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

#
#  File system related functions used in various places...
#

import os
import sys
import system


# Return directory list for provided path

def get_dirs(path='.'):
    list = []
    if path:
        if os.path.isdir(path):
            try:
                names = os.listdir(path)
            except os.error:
                return []
        names.sort()
        for name in names:
            if os.path.isdir(os.path.join(path, name)):
                list.append(name)
        return list


def get_dirs_withpath(path='.'):
    list = []
    names = []
    if os.path.isdir(path):
        try:
            names = os.listdir(path)
        except os.error:
            return names
    names.sort()
    for name in names:
        if os.path.isdir(os.path.join(path, name)) and not name == '.svn':
            list.append(os.path.join(path, name))
    return list


# Return file list for provided path
def get_files(path='.', ext='*'):
    list = []
    if path:
        if os.path.isdir(path):
            try:
                names = os.listdir(path)
            except os.error:
                return []
        names.sort()
        for name in names:
            if not os.path.isdir(os.path.join(path, name)):
                if ext == '*':
                    list.append(name)
                elif '.' + ext == name[-1 * (len(ext) + 1):]:
                    list.append(name)
    return list


# Return full file names list for provided path
def get_files_withpath(path='.', ext='*'):
    import glob
    if ext:
        if ext == '*':
            list = glob.glob(os.path.join(path, "*." + ext))
            list += glob.glob(os.path.join(path, "*"))
            list += glob.glob(os.path.join(path, ".*"))
        else:
            list = glob.glob(os.path.join(path, "*." + ext))
    else:
        list = glob.glob(os.path.join(path, "*"))
    list.sort()
    result = []
    for file in list:
        if os.path.isfile(file):
            result.append(file)
    return result


# Return recursive directories list for provided path
def get_dirs_tree(path='.'):
    tree = get_dirs_withpath(path)
    res = [] + tree
    for node in tree:
        subtree = get_dirs_tree(node)
        res += subtree
    return res


# Return recursive files list for provided path
def get_files_tree(path='.', ext='*'):
    tree = []
    dirs = [path, ]
    dirs += get_dirs_tree(path)
    for dir in dirs:
        list = get_files_withpath(dir, ext)
        list.sort()
        tree += list
    return tree


#
#	Filename manipulation
#

def find_in_path(paths, file):
    """
    The function finds a file FILE in one of the directories listed in PATHS. If a file
    is found, return its full name, None otherwise.
    """
    for path in paths:
        fullname = os.path.join(path, file)
        if os.path.isfile(fullname):
            return fullname


def find_files_in_path(paths, files):
    """
    The function finds one of the files listed in FILES in one of the directories in
    PATHS. Return the name of the first one found, None if no file is
    found.
    """
    for path in paths:
        for file in files:
            fullname = os.path.join(path, file)
            if os.path.isfile(fullname):
                return fullname


def xclear_dir(path):
    """
    Remove recursively all files and subdirectories from path.
    path directory is not removed. 
    """
    files = get_files_tree(path)
    for file in files:
        if os.path.lexists(file):
            os.remove(file)

    dirs = get_dirs_tree(path)
    for dir in dirs:
        if os.path.lexists(dir):
            os.rmdir(dir)


def xremove_dir(path):
    """
    Remove recursively all files and subdirectories from path
    including path directory. 
    """
    xclear_dir(path)
    os.removedirs(path)


def expanduser_unicode(path):
    """
    Fixes expanduser functionality for non-unicode platforms.
    """
    path = os.path.expanduser(path.encode(sys.getfilesystemencoding()))
    return path.decode(sys.getfilesystemencoding())


def path_unicode(path):
    return path.decode(sys.getfilesystemencoding())


def path_system(path):
    return path.encode(sys.getfilesystemencoding())


def get_system_fontdirs():
    """
    The function detects system font directories according to detected 
    system type.
    """
    if system.get_os_family() == system.LINUX:
        home = os.path.expanduser('~')
        return ['/usr/share/fonts', os.path.join(home, '.fonts')]
    if system.get_os_family() == system.WINDOWS:
        try:
            import _winreg
        except ImportError:
            return [os.path.join(os.environ['WINDIR'], 'Fonts'), ]
        else:
            k = _winreg.OpenKey(
                _winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
            )
            try:
                return [_winreg.QueryValueEx(k, "Fonts")[0], ]
            finally:
                _winreg.CloseKey(k)
    if system.get_os_family() == system.MACOSX:
        # FIXME: It's a stub. The paths should be more exact.
        return ['/', ]


DIRECTORY_OBJECT = 0
FILE_OBJECT = 1
UNKNOWN_OBJECT = 2

REGULAR_OBJECT = 0
LINK_OBJECT = 1


class FileObject:
    """
    The class represents file system object in UNIX-like style ('all are files').
    """
    type = FILE_OBJECT
    is_link = REGULAR_OBJECT
    is_hidden = 0
    ext = ''
    name = ''
    basename = ''

    def __init__(self, path):
        self.path = path
        if os.path.isdir(self.path):
            self.type = DIRECTORY_OBJECT
        elif os.path.isfile(self.path):
            self.type = FILE_OBJECT
        else:
            self.type = UNKNOWN_OBJECT

        if os.path.islink(self.path):
            self.is_link = LINK_OBJECT

        self.basename = os.path.basename(self.path)

        if not system.get_os_family() == system.WINDOWS:
            if self.basename[0] == '.':
                self.is_hidden = 1

        if self.type:
            if self.is_hidden:
                self.ext = os.path.splitext(self.basename[1:])[1][1:]
                self.name = os.path.splitext(self.basename[1:])[0]
            else:
                self.ext = os.path.splitext(self.basename)[1][1:]
                self.name = os.path.splitext(self.basename)[0]
        else:
            self.name = os.path.basename(self.path)


def get_file_objs(path):
    """
    Scans provided path for directories and files.
    On success returns a list of file objects.
    On error returns None.
    """
    if path[0] == '~':
        path = os.path.expanduser(path)
    if os.path.exists(path) and os.path.isdir(path):
        objs = []
        try:
            paths = os.listdir(path)
        except os.error:
            return None
        paths.sort()
        for item in paths:
            objs.append(FileObject(os.path.join(path, item)))
        result = []
        for obj in objs:
            if not obj.type: result.append(obj)
        for obj in objs:
            if obj.type: result.append(obj)
        return result
    return None


def get_file_extension(path):
    """
    Returns file extension without comma.
    """
    ext = os.path.splitext(path)[1]
    ext = ext.lower().replace('.', '')
    return ext


def change_file_extension(path, ext):
    filename = os.path.splitext(path)[0]
    ext = ext.lower().replace('.', '')
    return filename + '.' + ext

