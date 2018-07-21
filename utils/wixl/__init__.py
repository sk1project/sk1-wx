# -*- coding: utf-8 -*-
#
#   MSW MSI builder
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

"""
Supported features (WiX & wixl):
* JSON-driven MSI generation
* recursive app folder scanning
* msi package icon
* 32/64bit installations
* ProgramMenu folder and shortcuts
* OS version check
* x64 arch check
* custom conditions

Planned features:
* GUI for compiled msi-installers
* Extension associations (Open, Open with)
* add to system PATH
"""

import os
import sys
import tempfile

import wix

PROJECT = 'pyWiXL'
VERSION = '0.1'


def build(json_data, xml_only=False, stdout=False):
    json_data['_pkgname'] = PROJECT
    json_data['_pkgver'] = VERSION

    if 'Win64' in json_data:
        if json_data['Win64'] in [True, 'yes']:
            json_data['Win64'] = 'yes'
            json_data['_CheckX64'] = True
        else:
            json_data.pop('Win64')
            json_data['_CheckX64'] = False

    if '_OsCondition' in json_data:
        json_data['_OsCondition'] = str(json_data['_OsCondition'])

    output = json_data.get('_OutputName')
    if not output:
        raise Exception('Output filename is not defined!')
    if not xml_only and not output.endswith('.msi'):
        output += '.msi'
    elif xml_only and not output.endswith('.wxs'):
        output += '.wxs'
    output_path = os.path.join(json_data.get('_OutputDir', './'), output)

    if xml_only:
        if stdout:
            wix.Wix(json_data).write_xml(sys.stdout)
        else:
            print 'Writing XML into %s...' % output_path
            with open(output_path, 'wb') as fp:
                wix.Wix(json_data).write_xml(fp)
    elif wix.WIXL:
        xml_file = tempfile.NamedTemporaryFile(delete=True)
        with open(xml_file.name, 'wb') as fp:
            wix.Wix(json_data).write_xml(fp)
        arch = '-a x64' if json_data.get('Win64') else ''
        os.system('wixl -v %s -o %s %s' % (arch, output_path, xml_file.name))
    elif not wix.WIXL:
        raise Exception('WiX backend support is not implemented yet!')


if __name__ == "__main__":
    current_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.dirname(current_path)
    # wix.WIXL = False
    MSI_DATA = {
        # Required
        'Name': PROJECT,
        'UpgradeCode': '3AC4B4FF-10C4-4B8F-81AD-BAC3238BF690',
        'Version': VERSION,
        'Manufacturer': 'sK1 Project',
        # Optional
        'Description': '%s %s Installer' % (PROJECT, VERSION),
        'Comments': 'Licensed under GPLv3',
        'Keywords': 'msi, wix, build',
        'Win64': True,

        # Installation infrastructure
        '_OsCondition': 601,
        '_CheckX64': True,
        '_Conditions': [],  # [[msg,condition,level], ...]
        '_Icon': os.path.expanduser('~/Projects/pywixl.ico'),
        '_ProgramMenuFolder': 'sK1 Project',
        '_Shortcuts': [
            {'Name': PROJECT,
             'Description': 'Multiplatform MSI builder',
             'Target': '__init__.py'},
        ],
        '_SourceDir': path,
        '_InstallDir': 'wixl-%s' % VERSION,
        '_OutputName': '%s-%s-win64.msi' % (PROJECT.lower(), VERSION),
        '_OutputDir': os.path.expanduser('~'),
        '_SkipHidden': True,
    }
    build(MSI_DATA, xml_only=True, stdout=True)
    # build(MSI_DATA, xml_only=True)
    # build(MSI_DATA)
