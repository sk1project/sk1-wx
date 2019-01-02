# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017-2018 by Igor E. Novikov
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

import os
import sys

DEB = [
    'Ubuntu 14.04 32bit',
    'Ubuntu 14.04 64bit',
    'Ubuntu 16.04 32bit',
    'Ubuntu 16.04 64bit',
    # # 'Ubuntu 17.04 32bit',
    # # 'Ubuntu 17.04 64bit',
    'Ubuntu 17.10',
    # 'Ubuntu 18.04',
    'Debian 7.8 32bit',
    'Debian 7.8 64bit',
    'Debian 8.6 32bit',
    'Debian 8.6 64bit',
    'Debian 9.1 32bit',
    'Debian 9.1 64bit',
]
RPM = [
    'Fedora 25 32bit',
    'Fedora 25 64bit',
    'Fedora 26 32bit',
    'Fedora 26 64bit',
    'Fedora 27 32bit',
    'Fedora 27 64bit',
    'OpenSuse 42.1 64bit',
    'OpenSuse 42.2 64bit',
    'OpenSuse 42.3 64bit',
]
MSI = [
    'Win7 32bit',
    'Win7 64bit',
]

OSes = RPM + DEB #+ MSI

VMTYPE = 'headless'  # 'gui'

STDOUT_MAGENTA = '\033[95m'
STDOUT_BLUE = '\033[94m'
STDOUT_GREEN = '\033[92m'
STDOUT_YELLOW = '\033[93m'
STDOUT_FAIL = '\033[91m'
STDOUT_ENDC = '\033[0m'
STDOUT_BOLD = '\033[1m'
STDOUT_UNDERLINE = '\033[4m'


def fetch_cli_args(data_dict):
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        for item in args:
            if '=' in item:
                key, value = item.split('=')[:2]
                if value[0] in ('"', "'"):
                    value = value[1:]
                if value[-1] in ('"', "'"):
                    value = value[:-1]
                data_dict[key] = value


def echo_msg(msg, newline=True, flush=True, code=''):
    if newline:
        msg += '\n'
    if code:
        msg = code + msg + STDOUT_ENDC
    sys.stdout.write(msg)
    if flush:
        sys.stdout.flush()


def startvm(vmname):
    if vmname in MSI:
        os.system('VBoxManage startvm "%s" --type %s' % (vmname, 'gui'))
    else:
        os.system('VBoxManage startvm "%s" --type %s' % (vmname, VMTYPE))


def suspendvm(vmname):
    echo_msg('\nSUSPENDING "%s"' % vmname)
    os.system('VBoxManage controlvm "%s" savestate' % vmname)


def run_agent_deb(vmname, dataset):
    echo_msg('\n===>STARTING BUILD ON "%s"' % vmname, code=STDOUT_GREEN)
    cmd = 'VBoxManage --nologo guestcontrol "%s" run' % vmname
    cmd += ' --exe "/usr/bin/sudo"'
    cmd += ' --username "%s"' % dataset['user']
    cmd += ' --password "%s"' % dataset['user_pass']
    cmd += ' --wait-stdout --wait-stderr'
    cmd += ' -- sudo/arg0 "python2"'
    cmd += ' "/home/%s/build-agent.py"' % dataset['user']
    for item in dataset.keys():
        value = dataset[item]
        if not value:
            continue
        if ' ' in value:
            value = "'%s'" % value
        cmd += ' "%s=%s"' % (item, value)

    os.system(cmd)
    echo_msg('===>BUILD FINISHED ON "%s"' % vmname, code=STDOUT_GREEN)


def run_agent_rpm(vmname, dataset):
    echo_msg('\n===>STARTING BUILD ON "%s"' % vmname, code=STDOUT_GREEN)
    cmd = 'VBoxManage --nologo guestcontrol "%s" run' % vmname
    cmd += ' --exe "/usr/bin/python2"'
    cmd += ' --username "%s"' % dataset['user']
    cmd += ' --password "%s"' % dataset['user_pass']
    cmd += ' --wait-stdout --wait-stderr'
    cmd += ' -- python2/arg0'
    cmd += ' "/home/%s/build-agent.py"' % dataset['user']
    for item in dataset.keys():
        value = dataset[item]
        if not value:
            continue
        if ' ' in value:
            value = "'%s'" % value
        cmd += ' "%s=%s"' % (item, value)

    os.system(cmd)
    echo_msg('===>BUILD FINISHED ON "%s"' % vmname, code=STDOUT_GREEN)


def run_agent_windows(vmname, dataset):
    echo_msg('\n===>STARTING BUILD ON "%s"' % vmname, code=STDOUT_GREEN)
    cmd = 'VBoxManage --nologo guestcontrol "%s" run' % vmname
    cmd += ' --exe "c:\\python27\\python.exe"'
    cmd += ' --username "%s"' % dataset['user']
    cmd += ' --password "%s"' % dataset['user_pass']
    cmd += ' --wait-stdout --wait-stderr'
    cmd += ' -- sudo/arg0'
    cmd += ' "c:\\users\\%s\\build-agent.py"' % dataset['user']
    for item in dataset.keys():
        value = dataset[item]
        if not value:
            continue
        if ' ' in value:
            value = "'%s'" % value
        cmd += ' "%s=%s"' % (item, value)

    os.system(cmd)
    echo_msg('===>BUILD FINISHED ON "%s"' % vmname, code=STDOUT_GREEN)


def launch_farm(dataset, os_list=None):
    os_list = os_list or OSes
    flr_left = '\n' + '|' * 20
    flr_right = '|' * 20 + '\n'
    echo_msg(flr_left + ' FARM STARTED ' + flr_right, code=STDOUT_YELLOW)

    for vmname in os_list:
        echo_msg(vmname + '-' * 40 + '\n', code=STDOUT_BOLD)
        startvm(vmname)
        if vmname in MSI:
            run_agent_windows(vmname, dataset)
        elif vmname in RPM:
            run_agent_rpm(vmname, dataset)
        else:
            run_agent_deb(vmname, dataset)
        suspendvm(vmname)

    echo_msg(flr_left + 'FARM TERMINATED' + flr_right, code=STDOUT_YELLOW)
