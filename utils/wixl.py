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

import uuid

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
    'DirectoryRef': ('Id', ),
    'Component': ('Id', 'Guid', 'Win64'),
    'ComponentRef': ('Id', ),
    'File': ('Id', 'DiskId', 'Name', 'KeyPath', 'Source'),
    'Shortcut': ('Id', 'Name', 'Description', 'Target' 'WorkingDirectory'),
    'Feature': ('Id', 'Title', 'Level'),
}

INDENT = 4


class XmtElement(object):
    childs = None
    tag = None
    attrs = None
    comment = None

    def __init__(self, tag, **kwargs):
        self.childs = []
        self.tag = tag
        self.attrs = {key: value for key, value in kwargs
                      if key in ATTRS[self.tag]}
        if 'Id' not in self.attrs:
            self.attrs['Id'] = str(uuid.uuid4())

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
        for key, value in self.attrs:
            fp.write(' %s="%s"' % (key, value))
        if self.childs:
            fp.write('>\n')
            for child in self.childs:
                child.write(fp, indent + INDENT)
            fp.write('%s</%s>\n' % (tab, self.tag))
        else:
            fp.write(' />\n')


class Wix(XmtElement):
    tag = 'Wix'

    def __init__(self, data):
        self.source_dir = data.get('_SourceDir', '.')
        super(Wix, self).__init__(self.tag, **data)
