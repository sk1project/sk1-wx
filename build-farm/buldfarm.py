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

DEB = []
RPM = []
MSI = []

OSes = [
    'Ubuntu 14.04 32bit',
    'Ubuntu 14.04 64bit',
    'Ubuntu 16.04 32bit',
    'Ubuntu 16.04 64bit',
]

VMTYPE = 'gui'  # 'headless'


def startvm(vmname):
    print '===>STARTING "%s"' % vmname
    os.system('VBoxManage startvm "%s" --type %s' % (vmname, VMTYPE))
    print '===>"%s" WORKS!' % vmname


def suspendvm(vmname):
    print '===>SUSPENDING "%s"' % vmname
    os.system('VBoxManage controlvm "%s" savestate' % vmname)
    print '===>"%s" SUSPENDED!' % vmname

# VBoxManage guestcontrol <UUID> exec --image /bin/sh --username <su username> --password <su password> --wait-exit --wait-stdout --wait-stderr -- "[ -d /<server_folder>/ ] && echo "OK" || echo "Server is not installed""
def run_agent(vmname):
    cmd = 'VBoxManage guestcontrol "%s" exec ' % vmname
    cmd += ' --image /usr/bin/python'
    cmd += ' --user <su username>'
    cmd += ' --password <su password>'
    cmd += ' --wait-exit --wait-stdout --wait-stderr'