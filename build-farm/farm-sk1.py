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

import os

DATASET = {
    'mode': 'build',

    # release - to prepare release build
    # build - to build package only
    # test - to run in test mode
    'project': 'sk1-wx',
    'project2': 'sk1-wx-msw',
    'git_url': 'https://github.com/sk1project/sk1-wx',
    'git_url2': 'https://github.com/sk1project/sk1-wx-msw',
    'user': 'igor',
    'user_pass': '123',
    'sudo_user': 'igor',
    'sudo_pass': '123',
    'root_pass': '123',
    'ftp_url': '192.168.0.102',
    'ftp_path': '/home/igor/buildfarm',
    'ftp_user': 'igor',
    'ftp_pass': '',
    'timestamp': '',
    'script': 'setup-sk1.py',
}

DEB = [
    'Ubuntu 14.04 32bit',
    'Ubuntu 14.04 64bit',
    'Ubuntu 16.04 32bit',
    'Ubuntu 16.04 64bit',
    'Ubuntu 17.04 32bit',
    'Ubuntu 17.04 64bit',
    'Debian 7.8 32bit',
    'Debian 7.8 64bit',
    'Debian 8.6 32bit',
    'Debian 8.6 64bit',
]
RPM = [
    'Fedora 23 32bit',
    'Fedora 23 64bit',
    'Fedora 24 32bit',
    'Fedora 24 64bit',
    'OpenSuse 13.2 32bit',
    'OpenSuse 13.2 64bit',
    'OpenSuse 42.1 64bit',
]
MSI = [
    'Win7 32bit',
    'Win7 64bit',
]

OSes = DEB + RPM + MSI

VMTYPE = 'gui'  # 'headless'


def startvm(vmname):
    print '===>STARTING "%s"' % vmname
    os.system('VBoxManage startvm "%s" --type %s' % (vmname, VMTYPE))
    print '===>"%s" WORKS!' % vmname


def suspendvm(vmname):
    print '===>SUSPENDING "%s"' % vmname
    os.system('VBoxManage controlvm "%s" savestate' % vmname)
    print '===>"%s" SUSPENDED!' % vmname


def run_agent(vmname):
    print '===>STARTING BUILD ON "%s"' % vmname
    cmd = 'VBoxManage --nologo guestcontrol "%s" run' % vmname
    cmd += ' --exe "/usr/bin/python"'
    cmd += ' --username "%s"' % DATASET['user']
    cmd += ' --password "%s"' % DATASET['user_pass']
    cmd += ' --wait-stdout --wait-stderr'
    cmd += ' -- python/arg0 "/home/%s/build-agent-sk1.py"' % DATASET['user']
    counter = 1
    for item in DATASET.keys():
        value = DATASET[item]
        if not value:
            continue
        if ' ' in value:
            value = "'%s'" % value
        cmd += ' -- python/arg%d "%s=%s"' % (counter, item, value)
        counter += 1

    os.system(cmd)
    print '===>BUILD FINISHED ON "%s"' % vmname


for vmname in ['Ubuntu 14.04 32bit', ]:
    startvm(vmname)
    run_agent(vmname)
    suspendvm(vmname)
