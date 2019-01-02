# -*- coding: utf-8 -*-
#
#   Build utils
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
# 	along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import platform
import shutil
import sys

from . import fsutils


def get_resources(pkg_path, path):
    path = os.path.normpath(path)
    pkg_path = os.path.normpath(pkg_path)
    size = len(pkg_path) + 1
    dirs = fsutils.get_dirs_tree(path)
    dirs.append(path)
    res_dirs = []
    for item in dirs:
        res_dirs.append(os.path.join(item[size:], '*.*'))
    return res_dirs


def clear_build():
    """
    Clears build result.
    """
    if os.path.exists('build'):
        os.system('rm -rf build')


def clear_msw_build():
    """
    Clears build result on MS Windows.
    """
    shutil.rmtree('build', True)


def make_source_list(path, file_list=None):
    """
    Returns list of paths for provided file list.
    """
    if file_list is None:
        file_list = []
    ret = []
    for item in file_list:
        ret.append(os.path.join(path, item))
    return ret


INIT_FILE = '__init__.py'


def is_package(path):
    """
    Checks is provided directory a python package.
    """
    if os.path.isdir(path):
        marker = os.path.join(path, INIT_FILE)
        if os.path.isfile(marker):
            return True
    return False


def get_packages(path):
    """
    Collects recursively python packages.
    """
    packages = []
    items = []
    if os.path.isdir(path):
        try:
            items = os.listdir(path)
        except os.error:
            pass
        for item in items:
            if item.startswith('.'):
                continue
            folder = os.path.join(path, item)
            if is_package(folder):
                packages.append(folder)
                packages += get_packages(folder)
    packages.sort()
    return packages


def get_package_dirs(path='src', excludes=None):
    """
    Collects root packages.
    """
    if excludes is None:
        excludes = []
    dirs = {}
    items = []
    if os.path.isdir(path):
        try:
            items = os.listdir(path)
        except os.error:
            pass
        for item in items:
            if item in excludes:
                continue
            if item == '.svn':
                continue
            folder = os.path.join(path, item)
            if is_package(folder):
                dirs[item] = folder
    return dirs


def get_source_structure(path='src', excludes=None):
    """
    Returns recursive list of python packages.
    """
    if excludes is None:
        excludes = []
    pkgs = []
    for item in get_packages(path):
        res = item.replace('\\', '.').replace('/', '.').split('src.')[1]
        check = True
        for exclude in excludes:
            if len(res) >= len(exclude) and res[:len(exclude)] == exclude:
                check = False
                break
        if check:
            pkgs.append(res)
    return pkgs


def compile_sources(folder='build'):
    """
    Compiles python sources in build/ directory.
    """
    import compileall
    compileall.compile_dir(folder, quiet=1)


def copy_modules(modules, src_root='src'):
    """
    Copies native modules into src/
    The routine implements build_update command
    functionality and executed after "setup.py build" command.
    """
    version = '.'.join(sys.version.split()[0].split('.')[:2])
    machine = platform.machine()
    ext = '.so'
    prefix = 'build/lib.linux-' + machine + '-' + version
    marker = ''

    if os.name == 'nt' and platform.architecture()[0] == '32bit':
        prefix = 'build/lib.win32-' + version
        ext = '.pyd'
        marker = 'win32'
    elif os.name == 'nt' and platform.architecture()[0] == '64bit':
        prefix = 'build/lib.win-amd64-' + version
        ext = '.pyd'
        marker = 'win64'

    for item in modules:
        path = os.path.join(*item.name.split('.')) + ext
        src = os.path.join(prefix, path)
        dst = os.path.join(src_root, path)
        shutil.copy(src, dst)
        if os.name == 'nt':
            dst2 = os.path.join('%s-devres' % marker, 'pyd',
                                os.path.basename(src))
            if os.path.exists(dst2):
                os.remove(dst2)
            shutil.copy(src, dst)
        print '>>>Module %s has been copied to src/ directory' % path
