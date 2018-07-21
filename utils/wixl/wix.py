# -*- coding: utf-8 -*-
#
#   WiXL/WiX model
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

import os
import uuid

WIXL = os.name != 'nt'
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
    'Condition': ('Message', 'Level'),
}


def defaults():
    return {
        'Description': '---',
        'Comments': '-',
        'Keywords': '---',
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
        '_OsCondition': '601',
    }


def get_guid():
    return str(uuid.uuid4()).upper()


def get_id(prefix=''):
    return '%s%s' % (prefix, get_guid().replace('-', ''))


class WixElement(object):
    childs = None
    tag = None
    attrs = None
    comment = None
    is_file = False
    is_dir = False
    is_comp = False
    nl = False

    def __init__(self, tag, **kwargs):
        self.childs = []
        self.tag = tag
        self.attrs = {key: value for key, value in kwargs.items()
                      if key in ATTRS[self.tag]}
        if 'Id' not in self.attrs or self.attrs['Id'] == '*':
            self.attrs['Id'] = get_id()
        if self.attrs.get('Guid') == '*':
            self.attrs['Guid'] = get_guid()

    def add(self, child):
        self.childs.append(child)

    def set(self, **kwargs):
        self.attrs.update(kwargs)

    def pop(self, key):
        if key in self.attrs:
            self.attrs.pop(key)

    def write_xml(self, fp, indent=0):
        if self.nl:
            fp.write('\n')
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
                child.write_xml(fp, indent + INDENT)
            fp.write('%s</%s>\n' % (tab, self.tag))
        else:
            fp.write(' />\n')


class WixCondition(WixElement):
    tag = 'Condition'
    nl = True

    def __init__(self, msg, condition, level=None, comment=None):
        self.comment = comment
        self.condition = condition
        super(WixCondition, self).__init__(self.tag, Message=msg)
        if level:
            self.set(Level=str(level))
        self.pop('Id')

    def write_xml(self, fp, indent=0):
        if self.nl:
            fp.write('\n')
        tab = indent * ' '
        if self.comment:
            fp.write('%s<!-- %s -->\n' % (tab, self.comment))
        fp.write('%s<%s' % (tab, self.tag))
        prefix = '\n%s  ' % tab if len(self.attrs) > WRAP else ' '
        for key, value in self.attrs.items():
            fp.write('%s%s="%s"' % (prefix, key, value))
        if WIXL:
            condition = self.condition
            fp.write('>%s</%s>\n' % (condition, self.tag))
        else:
            tab_int = (indent + INDENT) * ' '
            condition = '%s<![CDATA[%s]]>' % (tab_int, self.condition)
            fp.write('>\n%s\n%s</%s>\n' % (condition, tab, self.tag))


OS_CONDITION = {
    '501': 'Windows XP, Windows Server 2003',
    '502': 'Windows Server 2003',
    '600': 'Windows Vista, Windows Server 2008',
    '601': 'Windows 7, Windows Server 2008R2',
    '602': 'Windows 8, Windows Server 2012',
}


class WixOsCondition(WixCondition):
    def __init__(self, os_condition):
        comment = 'Launch Condition to check suitable system version'
        os_condition = '501' if str(os_condition) not in OS_CONDITION \
            else str(os_condition)
        msg = 'This application is only ' \
              'supported on %s or higher.' % OS_CONDITION[os_condition]
        os_condition = 'Installed OR (VersionNT >= %s)' % os_condition
        super(WixOsCondition, self).__init__(msg, os_condition,
                                             comment=comment)


class WixArchCondition(WixCondition):
    def __init__(self):
        comment = 'Launch Condition to check that ' \
                  'x64 installer is used on x64 systems'
        msg = '64-bit operating system was not detected, ' \
              'please use the 32-bit installer.'
        super(WixArchCondition, self).__init__(msg, 'VersionNT64',
                                               comment=comment)


class WixProperty(WixElement):
    tag = 'Property'

    def __init__(self, pid, value):
        super(WixProperty, self).__init__(self.tag, Id=pid, Value=value)


class WixIcon(WixElement):
    tag = 'Icon'
    nl = True

    def __init__(self, data):
        self.source = data.get('_Icon', '')
        super(WixIcon, self).__init__(self.tag,
                                      SourceFile=data.get('_Icon', ''),
                                      Id=os.path.basename(self.source))


class WixMedia(WixElement):
    tag = 'Media'
    nl = True

    def __init__(self, data):
        super(WixMedia, self).__init__(self.tag, Id='1', **data)


class WixFile(WixElement):
    tag = 'File'
    path = None
    is_file = True

    def __init__(self, data, path, rel_path):
        self.path = path
        pid = get_id('fil')
        super(WixFile, self).__init__(self.tag, **data)
        self.set(Id=pid, Name=os.path.basename(rel_path), Source=path)


class WixComponent(WixElement):
    tag = 'Component'
    is_comp = True

    def __init__(self, data, path, rel_path):
        super(WixComponent, self).__init__(self.tag, Guid=get_guid(), **data)
        self.add(WixFile(data, path, rel_path))
        self.set(Id=get_id('cmp'))
        COMPONENTS.append(self.attrs['Id'])


class WixDirectory(WixElement):
    tag = 'Directory'
    is_dir = True

    def __init__(self, data=None, path=None, rel_path=None, **kwargs):
        name = kwargs['Name'] if 'Name' in kwargs \
            else os.path.basename(rel_path)
        pid = kwargs['Id'] if 'Id' in kwargs \
            else get_id('dir')
        super(WixDirectory, self).__init__(self.tag, Id=pid, Name=name)

        if data is not None:
            for item in os.listdir(path):
                if data.get('_SkipHidden') and item.startswith('.'):
                    continue
                item_path = os.path.join(path, item)
                item_rel_path = os.path.join(rel_path, item)
                if os.path.isdir(item_path):
                    self.add(WixDirectory(data, item_path, item_rel_path))
                elif os.path.isfile(item_path):
                    self.add(WixComponent(data, item_path, item_rel_path))


class WixInstallDir(WixElement):
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


class WixPfDir(WixElement):
    tag = 'Directory'
    is_dir = True

    def __init__(self, data):
        pid = 'ProgramFiles64Folder' if data.get('Win64') == 'yes' \
            else 'ProgramFilesFolder'
        super(WixPfDir, self).__init__(self.tag, Id=pid, Name='PFiles')
        self.add(WixInstallDir(data))


class WixTargetDir(WixElement):
    tag = 'Directory'
    is_dir = True
    nl = True

    def __init__(self, data):
        self.comment = 'Installed file tree'
        super(WixTargetDir, self).__init__(self.tag, Id='TARGETDIR',
                                           Name='SourceDir')
        self.add(WixPfDir(data))


class WixFeature(WixElement):
    tag = 'Feature'
    nl = True

    def __init__(self, data):
        super(WixFeature, self).__init__(self.tag,
                                         Title=data.get('Name'),
                                         Level='1')
        for item in COMPONENTS:
            self.add(WixComponentRef(Id=item))


class WixShortcut(WixElement):
    tag = 'Shortcut'

    def __init__(self, shortcut_data):
        super(WixShortcut, self).__init__(self.tag, **shortcut_data)


class WixRemoveFolder(WixElement):
    tag = 'RemoveFolder'

    def __init__(self, **kwargs):
        super(WixRemoveFolder, self).__init__(self.tag, **kwargs)


class WixRegistryValue(WixElement):
    tag = 'RegistryValue'

    def __init__(self, **kwargs):
        super(WixRegistryValue, self).__init__(self.tag, **kwargs)


class WixDirectoryRef(WixElement):
    tag = 'DirectoryRef'

    def __init__(self, **kwargs):
        super(WixDirectoryRef, self).__init__(self.tag, **kwargs)


class WixComponentRef(WixElement):
    tag = 'ComponentRef'

    def __init__(self, **kwargs):
        super(WixComponentRef, self).__init__(self.tag, **kwargs)


class WixShortcutComponent(WixElement):
    tag = 'Component'

    def __init__(self, data, shortcut_data):
        pid = get_id()
        guid = get_guid()
        super(WixShortcutComponent, self).__init__(self.tag, Guid=guid, **data)
        self.add(WixShortcut(shortcut_data))
        self.add(WixRemoveFolder(Id=shortcut_data['DirectoryRef'],
                                 On='uninstall'))
        reg_key = 'Software\\%s\\%s' % (data['Manufacturer'].replace(' ', '_'),
                                        data['Name'].replace(' ', '_'))
        self.add(WixRegistryValue(Root='HKCU', Key=reg_key,
                                  Name='installed', Type='integer',
                                  Value='1', KeyPath='yes'))
        self.set(Id='cmp%s' % pid)
        COMPONENTS.append(self.attrs['Id'])


class WixPackage(WixElement):
    tag = 'Package'

    def __init__(self, data):
        super(WixPackage, self).__init__(self.tag, **data)


class WixProduct(WixElement):
    tag = 'Product'

    def __init__(self, data):
        super(WixProduct, self).__init__(self.tag, **data)
        self.set(Id=get_guid())
        self.add(WixPackage(data))
        COMPONENTS[:] = []
        self.add(WixMedia(data))
        media_name = '%s %s Installation' % (data['Name'], data['Version'])
        self.add(WixProperty('DiskPrompt', media_name))

        if data.get('_OsCondition'):
            self.add(WixOsCondition(data['_OsCondition']))
        if data.get('_CheckX64'):
            self.add(WixArchCondition())
        if data.get('_Conditions'):
            for msg, cnd in data['_Conditions']:
                self.add(WixCondition(msg, cnd))

        if data.get('_Icon'):
            self.add(WixIcon(data))
            icon_name = os.path.basename(data['_Icon'])
            self.add(WixProperty('ARPPRODUCTICON', icon_name))
        target_dir = WixTargetDir(data)
        self.add(target_dir)

        if data.get('_Shortcuts') and data.get('_ProgramMenuFolder'):
            pm_dir = WixDirectory(Id='ProgramMenuFolder', Name='')
            pm_dir.pop('Name')
            pm_dir.comment = 'Application ProgramMenu folder'
            target_dir.add(pm_dir)
            shortcut_dir = WixDirectory(Id=get_id('mnu'),
                                        Name=data.get('_ProgramMenuFolder'))
            pm_dir.add(shortcut_dir)
            ref = shortcut_dir.attrs['Id']

            dir_ref = WixDirectoryRef(Id=ref)
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


class Wix(WixElement):
    tag = 'Wix'

    def __init__(self, data):
        self.msi_data = defaults()
        self.msi_data.update(data)
        self.source_dir = self.msi_data.get('_SourceDir', '.')
        super(Wix, self).__init__(self.tag, xmlns=XMLNS)
        self.pop('Id')
        self.add(WixProduct(self.msi_data))
        self.comment = 'Generated by %s %s' % \
                       (data['_pkgname'], data['_pkgver'])

    def write_xml(self, fp, indent=0):
        tab = indent * ' '
        fp.write('%s<?xml version="1.0" encoding="utf-8"?>\n' % tab)
        super(Wix, self).write_xml(fp, indent)
