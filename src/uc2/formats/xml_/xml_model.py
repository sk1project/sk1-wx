# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015-2016 by Igor E. Novikov
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


from uc2.formats.generic import TaggedModelObject


class XMLObject(TaggedModelObject):
    """
    Represents generic XML tree object.
    Object tag is stored in 'tag' field.
    Object attributes are in 'attrs' dict.
    'content' field contains object data. 
    """
    comments = ''
    attrs = {}
    content = ''

    def __init__(self, tag=''):
        self.childs = []
        self.attrs = {}
        self.comments = ''
        self.content = ''
        self.tag = ''
        if tag: self.tag = tag

    def is_content(self):
        return False

    def resolve(self):
        is_node = len(self.childs)
        info = ''
        if is_node: info = '%d' % (len(self.childs))
        return (not is_node, self.tag, info)


class XmlContentText(XMLObject):
    text = ''

    def __init__(self, text=''):
        self.text = text
        XMLObject.__init__(self, 'spacer')

    def is_content(self): return True
