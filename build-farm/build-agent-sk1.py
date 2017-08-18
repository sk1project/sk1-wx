#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#   Crossplatform build agent for VirtualBox build farm
#
#   Copyright (C) 2017 by Igor E. Novikov
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

#   SYNOPSIS
#   Agent assumes that git, compiler, python, dev-packages have been installed
#   on current build platform.
#
#   Agent gets on start following args:
#       project - unique project name
#       project2 - additional project name (msw/macos builds)
#       git_url - main repository URL
#       git_url2 - additional repository URL (msw/macos builds)
#       ftp_url - upload server url (ftp://host:port) 
#       ftp_path - path on remote ftp server     
#       ftp_user - upload server user
#       ftp_pass - ftp user pass
#       timestamp - optional build marker (like 20170624)
#
#   To execute sudo you need adding in /etc/sudoers following line:
#   username ALL = NOPASSWD: ALL

import datetime
import ftplib
import ntpath
import os
import platform
import sys
import time


class Error(Exception):
    pass


DATASET = {
    'mode': 'publish',
    # publish - to build and publish build result
    # release - to prepare release build
    # build - to build package only
    # test - to run in test mode
    'project': 'sk1-wx',
    'project2': 'sk1-wx-msw',
    'git_url': 'https://github.com/sk1project/sk1-wx',
    'git_url2': 'https://github.com/sk1project/sk1-wx-msw',
    'user': 'igor',
    'ftp_url': '192.168.0.102',
    'ftp_path': '/home/igor/buildfarm',
    'ftp_user': 'igor',
    'ftp_pass': '',
    'timeout': '10',
    'timestamp': datetime.datetime.now().strftime("%Y%m%d"),
    'script': 'setup-sk1.py',
}

WINDOWS = 'Windows'
LINUX = 'Linux'
MACOS = 'Darwin'


def is_msw():
    return platform.system() == WINDOWS


def is_linux():
    return platform.system() == LINUX


def is_macos():
    return platform.system() == MACOS


def is_path(pth):
    return os.path.lexists(pth)


MINT = 'LinuxMint'
UBUNTU = 'Ubuntu'
DEBIAN = 'debian'
FEDORA = 'fedora'
OPENSUSE = 'SuSE'

MARKERS = {
    MINT: 'mint',
    UBUNTU: 'ubuntu',
    DEBIAN: 'debian',
    FEDORA: 'fc',
    OPENSUSE: 'opensuse',
}


def is_deb():
    return platform.dist()[0] in [MINT, UBUNTU, DEBIAN]


def is_debian():
    return platform.dist()[0] == DEBIAN


def is_ubuntu():
    return platform.dist()[0] == UBUNTU


def is_rpm():
    return platform.dist()[0] in [FEDORA, OPENSUSE]


def echo_msg(msg, newline=True, flush=True):
    if newline:
        msg += '\n'
    sys.stdout.write(msg)
    if flush:
        sys.stdout.flush()


def get_marker():
    if is_linux():
        if is_deb():
            ver = platform.dist()[1]
            if is_debian():
                ver = ver.split('.')[0]
            marker = '_%s_%s_' % (MARKERS[platform.dist()[0]], ver)
            if DATASET['timestamp']:
                marker = '_%s%s' % (DATASET['timestamp'], marker)
            return marker
        elif is_rpm():
            ver = platform.dist()[1].split('.')[0]
            marker = MARKERS[platform.dist()[0]] + ver
            if DATASET['timestamp']:
                marker = '%s.%s' % (DATASET['timestamp'], marker)
            return marker
        return MARKERS[platform.dist()[0]]
    elif is_msw():
        # TODO: Should be implemented
        return 'win'
    return 'macos'


def get_package_name(pth):
    files = []
    file_items = os.listdir(pth)
    for file_item in file_items:
        if os.path.isfile(os.path.join(pth, file_item)):
            files.append(file_item)
    if is_deb():
        if len(files) == 1 and files[0].endswith('.deb'):
            return files[0]
    elif is_rpm():
        for file_item in files:
            if file_item.endswith('.rpm') and not file_item.endswith('src.rpm'):
                return file_item
    elif is_msw():
        # TODO: Should be implemented
        pass
    raise Error('Build failed! There is no build result.')


def command(exec_cmd):
    os.system(exec_cmd)


def fetch_cli_args():
    echo_msg('\nProcessing CLI args', False)
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        for item in args:
            if '=' in item:
                key, value = item.split('=')[:2]
                if value[0] in ('"', "'"):
                    value = value[1:]
                if value[-1] in ('"', "'"):
                    value = value[:-1]
                DATASET[key] = value
                echo_msg('.', False)
    echo_msg('...OK')


def check_su_mode():
    if is_msw():
        return
    if DATASET['su_mode'] != 'yes':
        return
    echo_msg('=====SUPERUSER MODE ON=====')
    time.sleep(2)
    items = DATASET.keys()
    args = []
    for item in items:
        value = DATASET[item]
        if not value or item == 'su_mode':
            continue
        if ' ' in value:
            value = '"%s"' % value
        args.append('%s=%s' % (item, value))
    args = ' '.join(args)
    name = __file__.split(os.path.sep)[-1]
    os.system('sudo python /home/%s/%s %s' % (
        DATASET['user'], name, args))
    echo_msg('\n=====SUPERUSER MODE OFF=====')
    sys.exit(0)


def check_mode():
    echo_msg('Checking mode', False)
    if DATASET['mode'] == 'test':
        echo_msg('\nDATASET:')
        items = DATASET.keys()
        items.sort()
        for item in items:
            value = DATASET[item]
            if not value:
                continue
            if ' ' in value:
                value = '"%s"' % value
            echo_msg('%s=%s' % (item, value))
        echo_msg('build dir: %s' % os.path.expanduser('~/buildfarm'))
        sys.exit()
    elif DATASET['mode'] == 'release':
        DATASET['timestamp'] = ''
    echo_msg('...OK')


def restart_network():
    if is_ubuntu():
        os.system('service network-manager restart 1> /dev/null')


def check_lan_connection():
    for item in ('ftp_pass', 'ftp_user', 'ftp_url', 'ftp_path'):
        if not DATASET[item]:
            echo_msg('There is no %s value!' % item)
            sys.exit(1)
    echo_msg('Checking LAN connection', False)
    counter = 0
    is_connection = False
    timeout = int(DATASET['timeout'])
    while counter < 5:
        try:
            session = ftplib.FTP(
                DATASET['ftp_url'],
                DATASET['ftp_user'],
                DATASET['ftp_pass'])
            session.quit()
            is_connection = True
        except:
            restart_network()
            counter += 1
            waitfor = counter * timeout
            echo_msg('...%ds' % waitfor, False)
            time.sleep(timeout)
        if is_connection:
            break
    if not is_connection:
        echo_msg(" ==> There is no LAN connection!")
        sys.exit(1)
    echo_msg('...OK')


def publish_file(pth):
    if DATASET['mode'] == 'build':
        return
    echo_msg('PUBLISHING ===> %s' % ntpath.basename(pth))
    session = ftplib.FTP(
        DATASET['ftp_url'],
        DATASET['ftp_user'],
        DATASET['ftp_pass'])
    session.cwd(DATASET['ftp_path'])
    fp = open(pth, 'rb')
    session.storbinary('STOR %s' % ntpath.basename(pth), fp)
    fp.close()
    session.quit()


# ------------ Build script ------------------

# CLI args processing
fetch_cli_args()
check_mode()

BUILD_DIR = os.path.expanduser('~/buildfarm')
PROJECT_DIR = os.path.join(BUILD_DIR, DATASET['project'])
PROJECT2_DIR = os.path.join(BUILD_DIR, DATASET['project2'])
DIST_DIR = os.path.join(PROJECT_DIR, 'dist')
if is_msw():
    DIST_DIR = os.path.join(PROJECT2_DIR, 'dist')
url = DATASET['git_url']
url2 = DATASET['git_url2']
script = DATASET['script']
proj_name = DATASET['project']
proj2_name = DATASET['project2']

if not is_path(BUILD_DIR):
    os.mkdir(BUILD_DIR)

# Check LAN connection
check_lan_connection()

# Package build procedure
if is_linux():
    package_name2 = ''
    old_name = ''
    new_name = ''
    if not is_path(PROJECT_DIR):
        echo_msg('Cloning project %s' % url)
        command('cd %s;git clone %s %s' % (BUILD_DIR, url, proj_name))
    else:
        echo_msg('Updating project %s' % url)
        command('cd %s;git pull' % PROJECT_DIR)
    if is_path(DIST_DIR):
        command('rm -rf %s' % DIST_DIR)

    if is_deb():
        echo_msg("Building DEB package")
        command(
            'cd %s;python %s bdist_deb 1> /dev/null' % (PROJECT_DIR, script))

        old_name = get_package_name(DIST_DIR)
        prefix, suffix = old_name.split('_')
        new_name = prefix + get_marker() + suffix
        if is_ubuntu():
            ts = ''
            if DATASET['timestamp']:
                ts = '_' + DATASET['timestamp']

            if platform.dist()[1] == '14.04':
                package_name2 = prefix + ts + '_mint_17_' + suffix
            elif platform.dist()[1] == '16.04':
                package_name2 = prefix + ts + '_mint_18_' + suffix

    elif is_rpm():
        echo_msg("Building RPM package")
        command(
            'cd %s;python %s bdist_rpm 1> /dev/null' % (PROJECT_DIR, script))

        old_name = get_package_name(DIST_DIR)
        items = old_name.split('.')
        new_name = '.'.join(items[:-2] + [get_marker(), ] + items[-2:])

    old_name = os.path.join(DIST_DIR, old_name)
    package_name = os.path.join(DIST_DIR, new_name)
    command('cp %s %s' % (old_name, package_name))
    publish_file(package_name)
    if package_name2:
        package_name2 = os.path.join(DIST_DIR, package_name2)
        command('cp %s %s' % (old_name, package_name2))
        publish_file(package_name2)


elif is_msw():
    # TODO: Implementation should be finished
    if not is_path(PROJECT_DIR):
        echo_msg('Cloning project %s' % url)
        command('cd %s;git clone %s %s' % (BUILD_DIR, url, proj_name))
    else:
        echo_msg('Updating projects %s' % url)
        command('cd %s;git pull' % PROJECT_DIR)
    if not is_path(PROJECT2_DIR):
        echo_msg('Cloning project %s' % url2)
        command('cd %s;git clone %s %s' % (BUILD_DIR, url, proj2_name))
    else:
        echo_msg('Updating projects %s' % url2)
        command('cd %s;git pull' % PROJECT2_DIR)
    if is_path(DIST_DIR):
        command('rm -rf %s' % DIST_DIR)

    command('cd %s;python %s bdist_msi' % (PROJECT2_DIR, script))
    command('cd %s;python %s bdist_portable' % (PROJECT2_DIR, script))
elif is_macos():
    pass
