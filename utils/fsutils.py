# -*- coding: utf-8 -*-
#
#   Filesystem utils
#
# 	Copyright (C) 2018 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os


def get_filenames(path='.', ext='*'):
    """
    Returns filename list for provided path filtering by extension.
    """
    result = []
    names = []
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
                    result.append(name)
                elif name.endswith('.' + ext):
                    result.append(name)
    return result


def get_filepaths(path='.', ext='*'):
    """
    Returns file path list for provided path filtering by extension.
    """
    import glob
    file_items = glob.glob(os.path.join(path, "*." + ext))
    file_items.sort()
    result = []
    for file_item in file_items:
        if os.path.isfile(file_item):
            result.append(file_item)
    return result


def get_dirpaths(path='.'):
    """
    Return directory path list for provided path
    """
    result = []
    names = []
    if os.path.isdir(path):
        try:
            names = os.listdir(path)
        except os.error:
            return names
    names.sort()
    for name in names:
        if os.path.isdir(os.path.join(path, name)) and not name.startswith('.'):
            result.append(os.path.join(path, name))
    return result


def get_dirs_tree(path='.'):
    """
    Returns recursive directory path list for provided path
    """
    tree = get_dirpaths(path)
    res = [] + tree
    for node in tree:
        subtree = get_dirs_tree(node)
        res += subtree
    return res


def get_files_tree(path='.', ext='*'):
    """
    Returns recursive file path list for provided path
    """
    tree = []
    dirs = [path, ]
    dirs += get_dirs_tree(path)
    for dir_item in dirs:
        files = get_filepaths(dir_item, ext)
        files.sort()
        tree += files
    return tree
