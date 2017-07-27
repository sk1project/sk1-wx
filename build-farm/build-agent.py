#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#   Crossplatform build agent for VirtualBox build farm
#
#	Copyright (C) 2017 by Igor E. Novikov
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

#   SYNOPSIS
#   Agent assumes that git, compiler, python, dev-packages have been installed
#   on current build platform.
#
#   Agent gets on start following args:
#       project - unique project name
#       project2 - additional project name (msw/macos builds)
#       git_url - main repository URL
#       git_url2 - additional repository URL (msw/macos builds)
#       ftp_url - url for build result upload (ftp://username:password@host:port)
#       timestamp - optional build marker (like 20170624)

import sys, os, platform

WINDOWS = 'Windows'
LINUX = 'Linux'
MACOS = 'Darwin'


def is_msw(): return platform.system() == WINDOWS
def is_linux(): return platform.system() == LINUX
def is_macos(): return platform.system() == MACOS
def is_path(path): return os.path.lexists(path)


BUILD_DIR = os.path.expanduser('~/buildfarm')

DATASET = {
    'project': 'sk1-wx',
    'project2': 'sk1-wx-msw',
    'git_url': 'https://github.com/sk1project/sk1-wx',
    'git_url2': '',
    'ftp_url': 'ftp://builder:password@192.168.0.102',
    'timestamp': ''
}

# CLI args processing
if len(sys.argv) > 1:
    args = sys.argv[1:]
    for item in args:
        if '=' in item:
            key, value = item.split('=')[:2]
            if value[0] in ('"', "'"): value = value[1:]
            if value[-1] in ('"', "'"): value = value[:-1]
            DATASET[key] = value

PROJECT_DIR = os.path.join(BUILD_DIR, DATASET['project'])
PROJECT2_DIR = os.path.join(BUILD_DIR, DATASET['project2'])

if not os.path.lexists(BUILD_DIR): os.mkdir(BUILD_DIR)
