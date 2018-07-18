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

WiX only features:
* OS version check
* x64 arch check

Planned features:
* GUI for compiled msi-installers
* Extension associations (Open, Open with)
"""

import os
import tempfile

from . import wix


def build(json_data, xml_only=False):
    output = json_data.get('_OutputName')
    if 'Win64' in json_data:
        if json_data['Win64'] in [True, 'yes']:
            json_data['Win64'] = 'yes'
            json_data['_CheckX64'] = True
        else:
            json_data.pop('Win64')
            json_data['_CheckX64'] = False
    if not output:
        raise Exception('Output filename is not defined!')
    if not xml_only and not output.endswith('.msi'):
        output += '.msi'
    elif xml_only and not output.endswith('.wxs'):
        output += '.wxs'

    output_path = os.path.join(json_data.get('_OutputDir', './'), output)

    if xml_only:
        with open(output_path, 'wb') as fp:
            wix.Wix(json_data).write(fp)
    elif wix.WIXL:
        xml_file = tempfile.NamedTemporaryFile(delete=True)
        with open(xml_file.name, 'wb') as fp:
            wix.Wix(json_data).write(fp)
        arch = '-a x64' if json_data.get('Win64') else ''
        os.system('wixl -v %s -o %s %s' % (arch, output_path, xml_file.name))
    elif not wix.WIXL:
        raise Exception('WiX backend support is not implemented yet!')


if __name__ == "__main__":
    MSI_DATA = {
        # Required
        'Name': 'sK1 2.0rc4',
        'UpgradeCode': '3AC4B4FF-10C4-4B8F-81AD-BAC3238BF693',
        'Version': '2.0 rc4',
        'Manufacturer': 'sK1 Project',
        # Optional
        'Description': 'sK1 2.0 Installer',
        'Comments': 'Licensed under GPLv3',
        'Keywords': 'Vector graphics, Prepress',
        'Win64': True,

        # Installation infrastructure
        '_OsCondition': '601',
        '_CheckX64': True,
        '_Icon': '~/Projects/sk1-icon.ico',
        '_ProgramMenuFolder': 'sK1 Project',
        '_Shortcuts': [
            {'Name': 'sK1 illustration program',
             'Description': 'Open source vector graphics editor',
             'Target': 'bin/deco.py'},
        ],
        '_SourceDir': '~/Projects/sk1',
        '_InstallDir': 'sK1 2.0rc4',
        '_OutputName': 'sk1-2.0rc4-win64.msi',
        '_OutputDir': '~/Projects',
    }
    build(MSI_DATA)  # , xml_only=True)
