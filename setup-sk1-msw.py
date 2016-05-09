# -*- coding: utf-8 -*-

#   Setup script for sK1 2.x on MS Windows
#
#     Copyright (C) 2016 by Igor E. Novikov
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Usage: 
--------------------------------------------------------------------------
 to build package:       python setup-sk1-msw.py build
--------------------------------------------------------------------------
 to create portable distribution:   python setup-sk1-msw.py bdist_portable
--------------------------------------------------------------------------
 Help on available distribution formats: --help-formats
"""

import os, sys, shutil, platform

import buildutils

def get_os_prefix():
    if platform.architecture()[0] == '32bit':
        return 'win32'
    return 'win64'

def get_res_path():
    return get_os_prefix() + '-devres'

def get_build_suffix():
    if platform.architecture()[0] == '32bit':
        return '.win32-2.7'
    return '.win64-2.7'


############################################################
# Flags
############################################################
UPDATE_MODULES = False
PORTABLE_PACKAGE = False
CLEAR_BUILD = False

############################################################
# Package description
############################################################
NAME = 'sk1'
VERSION = '2.0RC1'
DESCRIPTION = 'Vector graphics editor for prepress'
AUTHOR = 'Igor E. Novikov'
AUTHOR_EMAIL = 'igor.e.novikov@gmail.com'
MAINTAINER = AUTHOR
MAINTAINER_EMAIL = AUTHOR_EMAIL
LICENSE = 'GPL v3'
URL = 'http://sk1project.org'
DOWNLOAD_URL = URL
CLASSIFIERS = [
'Development Status :: 5 - Stable',
'Environment :: Desktop',
'Intended Audience :: End Users/Desktop',
'License :: OSI Approved :: LGPL v2',
'License :: OSI Approved :: GPL v3',
'Operating System :: POSIX',
'Operating System :: MacOS :: MacOS X',
'Operating System :: Microsoft :: Windows',
'Programming Language :: Python',
'Programming Language :: C',
"Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
]
LONG_DESCRIPTION = '''
sK1 is an open source vector graphics editor similar to CorelDRAW, 
Adobe Illustrator, or Freehand. First of all sK1 is oriented for prepress 
industry, therefore works with CMYK colorspace and produces CMYK-based PDF 
and postscript output.
sK1 Project (http://sk1project.org),
Copyright (C) 2007-2016 by Igor E. Novikov 
'''

############################################################
# Build data
############################################################
src_path = 'src'
res_path = get_res_path()
include_path = os.path.join(res_path, 'include')
lib_path = [os.path.join(res_path, 'libs'), ]
modules = []

dirs = buildutils.get_dirs_tree('src/sk1/share')
share_dirs = []
for item in dirs: share_dirs.append(os.path.join(item[8:], '*.*'))

package_data = {
'sk1': share_dirs,
}

############################################################
# Main build procedure
############################################################

if len(sys.argv) == 1:
    print 'Please specify build options!'
    print __doc__
    sys.exit(0)

if len(sys.argv) > 1:
    if sys.argv[1] == 'bdist_portable':
        PORTABLE_PACKAGE = True
        CLEAR_BUILD = True
        sys.argv[1] = 'build'

    if sys.argv[1] == 'build_update':
        UPDATE_MODULES = True
        CLEAR_BUILD = True
        sys.argv[1] = 'build'

data_files = scripts = []

############################################################
# Native extensions
############################################################
from native_mods import make_modules

modules += make_modules(src_path, include_path, lib_path)

############################################################
# Setup routine
############################################################
from distutils.core import setup


setup(name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    license=LICENSE,
    url=URL,
    download_url=DOWNLOAD_URL,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    packages=buildutils.get_source_structure(),
    package_dir=buildutils.get_package_dirs(),
    package_data=package_data,
    data_files=data_files,
    scripts=scripts,
    ext_modules=modules)

############################################################
# .py source compiling
############################################################
if not UPDATE_MODULES:
    buildutils.compile_sources()

############################################################
# This section for developing purpose only
# Command 'python setup.py build_update' allows
# automating build and native extension copying
# into package directory
############################################################
if UPDATE_MODULES: buildutils.copy_modules(modules)

############################################################
# Implementation of bdist_portable command
############################################################
if PORTABLE_PACKAGE:
    print 40 * '#'
    print 'PORTABLE_PACKAGE'
    print 40 * '#'
    PKGS = ['sk1', 'uc2', 'wal']
    portable_name = '%s-%s-%s-portable' % (NAME, VERSION, get_os_prefix())
    libdir = os.path.join('build', 'lib' + get_build_suffix())

    os.mkdir(portable_name)

    from zipfile import ZipFile
    portable = os.path.join(get_res_path(), 'portable.zip')
    print 'Extracting', portable
    ZipFile(portable, 'r').extractall(portable_name)
    portable_libs = os.path.join(portable_name, 'libs')
    for item in PKGS:
        src = os.path.join(libdir, item)
        print 'Copying tree', src
        shutil.copytree(src, os.path.join(portable_libs, item))

    if not os.path.isdir('dist'): os.mkdir('dist')
    portable = os.path.join('dist', portable_name + '.zip')
    ziph = ZipFile(portable, 'w')

    for root, dirs, files in os.walk(portable_name):
        for item in files:
            path = os.path.join(root, item)
            print 'Compressing', path
            ziph.write(path)
    ziph.close()
    shutil.rmtree(portable_name, True)

if CLEAR_BUILD: buildutils.clear_msw_build()
