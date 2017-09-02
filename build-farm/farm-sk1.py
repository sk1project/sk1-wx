#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#   Build orchestrator for VirtualBox build farm
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

#   VBox guest preparation
#   1.Install required headers and tools
#   2.Install VBox Guest Addons
#       for Ubuntu just insert addons disk and do autorun
#       for Debian:
#           1)Install required packages with:
#               apt-get install build-essential module-assistant
#           2)Configure your system for building kernel modules by running:
#               m-a prepare
#           3)Run sh VBoxLinuxAdditions.run
#        for OpenSuse:
#           1)Update system:
#               sudo zypper refresh;sudo zypper update
#           2)Install tools for kernel module build:
#               sudo zypper in kernel-syms gcc make rpm-build
#           3)Insert addons disk and do autorun
#        for Fedora
#           1)Update system:
#               dnf update
#           2)Install tools for kernel module build:
#               dnf -y install gcc automake make kernel-headers kernel-devel
#               dnf -y install dkms bzip2 perl rpm-build
#   3.Copy build-agent.py to home dir
#   4.To execute sudo you need adding in /etc/sudoers following line:
#       username ALL = NOPASSWD: ALL

import datetime
import os
import sys

STDOUT_MAGENTA = '\033[95m'
STDOUT_BLUE = '\033[94m'
STDOUT_GREEN = '\033[92m'
STDOUT_YELLOW = '\033[93m'
STDOUT_FAIL = '\033[91m'
STDOUT_ENDC = '\033[0m'
STDOUT_BOLD = '\033[1m'
STDOUT_UNDERLINE = '\033[4m'

DATASET = {
    'agent_ver': '1.0.6',
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
    'user_pass': '123',
    'ftp_url': '192.168.0.102',
    'ftp_path': '/home/igor/buildfarm',
    'ftp_user': 'igor',
    'ftp_pass': 'Hes 6exks',
    'timestamp': datetime.datetime.now().strftime("%Y%m%d"),
    'script': 'setup-sk1.py',
}

DEB = [
    # 'Ubuntu 14.04 32bit',
    # 'Ubuntu 14.04 64bit',
    # 'Ubuntu 16.04 32bit',
    # 'Ubuntu 16.04 64bit',
    # 'Ubuntu 17.04 32bit',
    # 'Ubuntu 17.04 64bit',
    # 'Debian 7.8 32bit',
    # 'Debian 7.8 64bit',
    # 'Debian 8.6 32bit',
    # 'Debian 8.6 64bit',
    # 'Debian 9.1 32bit',
    # 'Debian 9.1 64bit',
]
RPM = [
    'Fedora 25 32bit',
    # 'Fedora 25 64bit',
    # 'Fedora 26 32bit',
    # 'Fedora 26 64bit',
    # 'OpenSuse 42.1 64bit',
    # 'OpenSuse 42.2 64bit',
    # 'OpenSuse 42.3 64bit',
]
MSI = [
    # 'Win7 32bit',
    # 'Win7 64bit',
]

OSes = DEB + RPM + MSI

VMTYPE = 'headless'  # 'gui'


def echo_msg(msg, newline=True, flush=True, code=''):
    if newline:
        msg += '\n'
    if code:
        msg = code + msg + STDOUT_ENDC
    sys.stdout.write(msg)
    if flush:
        sys.stdout.flush()


def startvm(vmname):
    os.system('VBoxManage startvm "%s" --type %s' % (vmname, VMTYPE))


def suspendvm(vmname):
    echo_msg('\nSUSPENDING "%s"' % vmname)
    os.system('VBoxManage controlvm "%s" savestate' % vmname)


def run_agent(vmname):
    echo_msg('\n===>STARTING BUILD ON "%s"' % vmname, code=STDOUT_GREEN)
    cmd = 'VBoxManage --nologo guestcontrol "%s" run' % vmname
    cmd += ' --exe "/usr/bin/sudo"'
    cmd += ' --username "%s"' % DATASET['user']
    cmd += ' --password "%s"' % DATASET['user_pass']
    cmd += ' --wait-stdout --wait-stderr'
    cmd += ' -- sudo/arg0 "python"'
    cmd += ' "/home/%s/build-agent.py"' % DATASET['user']
    for item in DATASET.keys():
        value = DATASET[item]
        if not value:
            continue
        if ' ' in value:
            value = "'%s'" % value
        cmd += ' "%s=%s"' % (item, value)

    os.system(cmd)
    echo_msg('===>BUILD FINISHED ON "%s"' % vmname, code=STDOUT_GREEN)


flr_left = '\n' + '|' * 20
flr_right = '|' * 20 + '\n'
echo_msg(flr_left + ' FARM STARTED ' + flr_right, code=STDOUT_YELLOW)

for vmname in OSes:
    echo_msg(vmname + '-' * 40 + '\n', code=STDOUT_BOLD)
    startvm(vmname)
    run_agent(vmname)
    suspendvm(vmname)

echo_msg(flr_left + 'FARM TERMINATED' + flr_right, code=STDOUT_YELLOW)
