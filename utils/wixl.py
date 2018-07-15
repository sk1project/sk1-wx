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
Supported features:

* recursive app folder scanning
* msi package icon
* 32/64bit installations
* ProgramMenu folder and shortcuts

"""

import os
import sys
import uuid

WIXL = os.name != 'nt'
PROJECT = 'pyWiXL'
VERSION = '0.1'
XMLNS = 'http://schemas.microsoft.com/wix/2006/wi'
INDENT = 4
WRAP = 3

COMPONENTS = []

ATTRS = {
    'Wix': ('xmlns',),
    'Product': ('Id', 'Name', 'UpgradeCode', 'Language', 'Codepage', 'Version',
                'Manufacturer'),
    'Package': ('Id', 'Keywords', 'Description', 'Comments', 'InstallerVersion',
                'Languages', 'Compressed', 'Manufacturer', 'SummaryCodepage'),
    'Media': ('Id', 'Cabinet', 'EmbedCab', 'DiskPrompt'),
    'Property': ('Id', 'Value',),
    'Icon': ('Id', 'SourceFile',),
    'Directory': ('Id', 'Name',),
    'DirectoryRef': ('Id',),
    'Component': ('Id', 'Guid', 'Win64'),
    'ComponentRef': ('Id',),
    'File': ('Id', 'DiskId', 'Name', 'KeyPath', 'Source'),
    'Shortcut': ('Id', 'Name', 'Description', 'Target', 'WorkingDirectory'),
    'Feature': ('Id', 'Title', 'Level'),
    'RemoveFolder': ('Id', 'On'),
    'RegistryValue': ('Root', 'Key', 'Name', 'Type', 'Value', 'KeyPath'),
}


def defaults():
    return {
        # Language
        'Language': '1033',
        'Languages': '1033',
        'Codepage': '1252',
        # Internals
        'InstallerVersion': '200',
        'Compressed': 'yes',
        'KeyPath': 'yes',
        # Media
        'Cabinet': 'Sample.cab',
        'EmbedCab': 'yes',
        'DiskPrompt': 'CD-ROM #1',
        'DiskId': '1',
        '_SkipHidden': True,
    }


class XmlElement(object):
    childs = None
    tag = None
    attrs = None
    comment = None
    is_file = False
    is_dir = False
    is_comp = False

    def __init__(self, tag, **kwargs):
        self.childs = []
        self.tag = tag
        self.attrs = {key: value for key, value in kwargs.items()
                      if key in ATTRS[self.tag]}
        if 'Id' not in self.attrs:
            self.attrs['Id'] = str(uuid.uuid4()).replace('-', '').upper()

    def add(self, child):
        self.childs.append(child)

    def set(self, **kwargs):
        self.attrs.update(kwargs)

    def pop(self, key):
        if key in self.attrs:
            self.attrs.pop(key)

    def write(self, fp, indent=0):
        tab = indent * ' '
        if self.comment:
            fp.write('%s<!-- %s -->\n' % (tab, self.comment))
        fp.write('%s<%s' % (tab, self.tag))
        prefix = '\n%s  ' % tab if len(self.attrs) > WRAP else ' '
        for key, value in self.attrs.items():
            fp.write('%s%s="%s"' % (prefix, key, value))
        if self.childs:
            fp.write('>\n')
            for child in self.childs:
                child.write(fp, indent + INDENT)
            fp.write('%s</%s>\n' % (tab, self.tag))
        else:
            fp.write(' />\n')


class WixIcon(XmlElement):
    tag = 'Icon'

    def __init__(self, data):
        self.source = data.get('_Icon', '')
        super(WixIcon, self).__init__(self.tag,
                                      SourceFile=data.get('_Icon', ''),
                                      Id=os.path.basename(self.source))

    def write(self, fp, indent=0):
        fp.write('\n')
        super(WixIcon, self).write(fp, indent)
        fp.write('%s<Property Id="ARPPRODUCTICON" Value="%s" />\n' %
                 (indent * ' ', os.path.basename(self.source)))


class WixMedia(XmlElement):
    tag = 'Media'

    def __init__(self, data):
        self.msi_data = data
        super(WixMedia, self).__init__(self.tag, **data)

    def write(self, fp, indent=0):
        fp.write('\n')
        super(WixMedia, self).write(fp, indent)
        fp.write('%s<Property Id="DiskPrompt" Value="%s Installation" />\n' %
                 (indent * ' ', self.msi_data.get('Version', '1.0')))


class WixFile(XmlElement):
    tag = 'File'
    path = None
    is_file = True

    def __init__(self, data, path, rel_path):
        self.path = path
        pid = str(uuid.uuid4()).replace('-', '').upper()
        super(WixFile, self).__init__(self.tag, **data)
        self.set(Id='fil%s' % pid,
                 Name=os.path.basename(rel_path),
                 Source=path)


class WixComponent(XmlElement):
    tag = 'Component'
    is_comp = True

    def __init__(self, data, path, rel_path):
        pid = str(uuid.uuid4()).replace('-', '').upper()
        super(WixComponent, self).__init__(self.tag,
                                           Guid=str(uuid.uuid4()).upper(),
                                           **data)
        self.add(WixFile(data, path, rel_path))
        self.set(Id='cmp%s' % pid)
        COMPONENTS.append(self.attrs['Id'])


class WixDirectory(XmlElement):
    tag = 'Directory'
    is_dir = True

    def __init__(self, data, path, rel_path):
        name = os.path.basename(rel_path)
        pid = str(uuid.uuid4()).replace('-', '').upper()
        super(WixDirectory, self).__init__(self.tag,
                                           Id='dir%s' % pid,
                                           Name=name)

        for item in os.listdir(path):
            if data.get('_SkipHidden') and item.startswith('.'):
                continue
            item_path = os.path.join(path, item)
            item_rel_path = os.path.join(rel_path, item)
            if os.path.isdir(item_path):
                self.add(WixDirectory(data, item_path, item_rel_path))
            elif os.path.isfile(item_path):
                self.add(WixComponent(data, item_path, item_rel_path))

    def write(self, fp, indent=0):
        if self.childs:
            super(WixDirectory, self).write(fp, indent)


class WixInstallDir(XmlElement):
    tag = 'Directory'
    is_dir = True

    def __init__(self, data):
        super(WixInstallDir, self).__init__(self.tag, Id='INSTALLDIR',
                                            Name=data.get('_InstallDir'))
        path = data.get('_SourceDir')
        rel_path = os.path.basename(path)
        # Recursive scan start
        for item in os.listdir(path):
            if data.get('_SkipHidden') and item.startswith('.'):
                continue
            item_path = os.path.join(path, item)
            item_rel_path = os.path.join(rel_path, item)
            if os.path.isdir(item_path):
                self.add(WixDirectory(data, item_path, item_rel_path))
            elif os.path.isfile(item_path):
                self.add(WixComponent(data, item_path, item_rel_path))


class WixPfDir(XmlElement):
    tag = 'Directory'
    is_dir = True

    def __init__(self, data):
        pid = 'ProgramFiles64Folder' if data.get('Win64') == 'yes' \
            else 'ProgramFilesFolder'
        super(WixPfDir, self).__init__(self.tag, Id=pid, Name='PFiles')
        self.add(WixInstallDir(data))


class WixTargetDir(XmlElement):
    tag = 'Directory'
    is_dir = True

    def __init__(self, data):
        super(WixTargetDir, self).__init__(self.tag, Id='TARGETDIR',
                                           Name='SourceDir')
        self.add(WixPfDir(data))

    def write(self, fp, indent=0):
        fp.write('\n')
        super(WixTargetDir, self).write(fp, indent)
        fp.write('\n')


class WixFeature(XmlElement):
    tag = 'Feature'

    def __init__(self, data):
        super(WixFeature, self).__init__(self.tag,
                                         Title=data.get('Name'),
                                         Level='1')
        for item in COMPONENTS:
            self.add(XmlElement('ComponentRef', Id=item))


class WixShortcut(XmlElement):
    tag = 'Shortcut'

    def __init__(self, shortcut_data):
        super(WixShortcut, self).__init__(self.tag, **shortcut_data)


class WixShortcutComponent(XmlElement):
    tag = 'Component'

    def __init__(self, data, shortcut_data):
        pid = str(uuid.uuid4()).replace('-', '').upper()
        guid = str(uuid.uuid4()).upper()
        super(WixShortcutComponent, self).__init__(self.tag, Guid=guid, **data)
        self.add(WixShortcut(shortcut_data))
        self.add(XmlElement('RemoveFolder',
                            Id=shortcut_data['DirectoryRef'],
                            On='uninstall'))
        reg_key = 'Software\\%s\\%s' % (data['Manufacturer'].replace(' ', '_'),
                                        data['Name'].replace(' ', '_'))
        self.add(XmlElement('RegistryValue', Root='HKCU', Key=reg_key,
                            Name='installed', Type='integer',
                            Value='1', KeyPath='yes'))
        self.set(Id='cmp%s' % pid)
        COMPONENTS.append(self.attrs['Id'])


class WixPackage(XmlElement):
    tag = 'Package'

    def __init__(self, data):
        self.msi_data = data
        super(WixPackage, self).__init__(self.tag, **data)
        COMPONENTS[:] = []
        self.add(WixMedia(data))
        if data.get('_Icon'):
            self.add(WixIcon(data))
        target_dir = WixTargetDir(data)
        self.add(target_dir)

        if data.get('_Shortcuts') and data.get('_ProgramMenuFolder'):
            pm_dir = XmlElement('Directory', Id='ProgramMenuFolder')
            pm_dir.comment = 'Application ProgramMenu folder'
            target_dir.add(pm_dir)
            shortcut_dir = XmlElement('Directory',
                                      Name=data.get('_ProgramMenuFolder'))
            pm_dir.add(shortcut_dir)
            ref = shortcut_dir.attrs['Id']

            dir_ref = XmlElement('DirectoryRef', Id=ref)
            self.add(dir_ref)
            for shortcut in data.get('_Shortcuts'):
                target = os.path.join(data['_SourceDir'], shortcut['Target'])
                work_dir_id, target_id = self.find_by_path(target_dir, target)
                shortcut_data = {
                    'DirectoryRef': ref,
                    'WorkingDirectory': work_dir_id,
                }
                shortcut_data.update(shortcut)
                shortcut_data['Target'] = '[#%s]' % target_id
                dir_ref.add(WixShortcutComponent(data, shortcut_data))

        if COMPONENTS:
            self.add(WixFeature(data))

    def find_by_path(self, parent, path):
        work_dir_id = target_id = None
        for item in parent.childs:
            if item.is_comp and item.childs[0].path == path:
                work_dir_id = parent.attrs['Id']
                target_id = item.childs[0].attrs['Id']
                return work_dir_id, target_id
            elif item.is_dir:
                work_dir_id, target_id = self.find_by_path(item, path)
                if work_dir_id is not None:
                    return work_dir_id, target_id
        return work_dir_id, target_id


class WixProduct(XmlElement):
    tag = 'Product'

    def __init__(self, data):
        super(WixProduct, self).__init__(self.tag, **data)
        self.add(WixPackage(data))


class Wix(XmlElement):
    tag = 'Wix'

    def __init__(self, data):
        self.msi_data = defaults()
        self.msi_data.update(data)
        self.source_dir = self.msi_data.get('_SourceDir', '.')
        super(Wix, self).__init__(self.tag, xmlns=XMLNS)
        self.pop('Id')
        self.add(WixProduct(self.msi_data))
        self.comment = 'Generated by %s %s' % (PROJECT, VERSION)

    def write(self, fp, indent=0):
        tab = indent * ' '
        fp.write('%s<?xml version="1.0" encoding="windows-1252"?>\n' % tab)
        super(Wix, self).write(fp, indent)


if __name__ == "__main__":
    MSI_DATA = {
        # Required
        'Name': 'sK1 2.0rc4',
        'UpgradeCode': '3AC4B4FF-10C4-4B8F-81AD-BAC3238BF693',
        'Version': '2.0rc4',
        'Manufacturer': 'sK1 Project',
        # Optional
        'Description': 'sK1 2.0 Installer',
        'Comments': 'Licensed under GPLv3',
        'Keywords': 'Vector graphics, Prepress',
        'Win64': 'yes',

        # Structural elements
        '_Icon': '/win32-devres/sk1.ico',
        '_ProgramMenuFolder': 'sK1 Project',
        '_Shortcuts': [
            {'Name': 'sK1 illustration program',
             'Description': 'Open source vector graphics editor',
             'Target': 'bin/deco.py'},
        ],
        '_SourceDir': '/home/igor/Projects/tests',
        '_InstallDir': 'sk1-2.0rc4',
        '_OutputName': 'sk1-2.0rc4-win64.msi',
    }
    Wix(MSI_DATA).write(sys.stdout)
