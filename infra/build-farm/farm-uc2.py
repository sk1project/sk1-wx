#!/usr/bin/env python2
#
# -*- coding: utf-8 -*-
#
#   UC2 build orchestrator for VirtualBox build farm
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
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

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

from farmutils import fetch_cli_args, launch_farm

DATASET = {
    'agent_ver': '1.1.9',
    'mode': 'publish',
    # publish - to build and publish build result
    # release - to prepare release build
    # build - to build package only
    # test - to run in test mode
    'app_name': 'uniconvertor',
    'app_ver': '2.0rc4',
    'project': 'sk1-wx',
    'project2': 'uc2-msw',
    'git_url': 'https://github.com/sk1project/sk1-wx',
    'git_url2': 'https://github.com/sk1project/uc2-msw',
    'user': 'igor',
    'user_pass': '123',
    'ftp_url': '192.168.0.102',
    'ftp_path': '/home/igor/buildfarm2',
    'ftp_user': 'igor',
    'ftp_pass': '',
    'timestamp': datetime.datetime.now().strftime("%Y%m%d"),
    'script': 'setup-uc2.py',
    'script2': 'setup-uc2-msw.py',
}

fetch_cli_args(DATASET)
launch_farm(DATASET)
