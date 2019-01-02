# -*- coding: utf-8 -*-
#
#  Copyright (C) 2012 by Igor E. Novikov
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

import logging

import xml.sax
from xml.sax import handler
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import InputSource

from uc2.utils.fs import path_system, path_unicode
from uc2.utils import fsutils
from uc2.utils.fsutils import get_fileptr

LOG = logging.getLogger(__name__)

IDENT = '\t'


def encode_quotes(line):
    result = line.replace('"', '&quot;')
    result = result.replace("'", "&#039;")
    return result


def decode_quotes(line):
    result = line.replace('&quot;', '"')
    result = result.replace("&#039;", "'")
    return result


def escape_quote(line):
    ret = line.replace("\\", "\\\\")
    return ret.replace("'", "\\'")


class XmlConfigParser(object):
    """
    Represents parent class for application config.
    """
    filename = ''

    def update(self, cnf=None):
        cnf = cnf or {}
        if cnf:
            for key in cnf.keys():
                if hasattr(self, key):
                    setattr(self, key, cnf[key])

    def load(self, filename=None):
        self.filename = filename
        if fsutils.lexists(filename):
            content_handler = XMLPrefReader(pref=self)
            error_handler = ErrorHandler()
            entity_resolver = EntityResolver()
            dtd_handler = DTDHandler()
            try:
                input_file = get_fileptr(filename)
                input_source = InputSource()
                input_source.setByteStream(input_file)
                xml_reader = xml.sax.make_parser()
                xml_reader.setContentHandler(content_handler)
                xml_reader.setErrorHandler(error_handler)
                xml_reader.setEntityResolver(entity_resolver)
                xml_reader.setDTDHandler(dtd_handler)
                xml_reader.parse(input_source)
                input_file.close()
            except Exception as e:
                LOG.error('Cannot read preferences from %s %s', filename, e)

    def save(self, filename=None):
        if self.filename and filename is None:
            filename = self.filename
        if len(self.__dict__) == 0 or filename is None:
            return

        try:
            fileobj = get_fileptr(filename, True)
        except Exception as e:
            LOG.error('Cannot write preferences into %s %s', filename, e)
            return

        writer = XMLGenerator(out=fileobj, encoding=self.system_encoding)
        writer.startDocument()
        defaults = XmlConfigParser.__dict__
        items = self.__dict__.items()
        items.sort()
        writer.startElement('preferences', {})
        writer.characters('\n')
        for key, value in items:
            if key in defaults and defaults[key] == value:
                continue
            if key in ['filename', 'app']:
                continue
            writer.characters('\t')
            writer.startElement('%s' % key, {})

            str_value = path_unicode(value.__str__())
            if isinstance(value, str):
                str_value = "'%s'" % (escape_quote(str_value))

            writer.characters(str_value)

            writer.endElement('%s' % key)
            writer.characters('\n')
        writer.endElement('preferences')
        writer.endDocument()
        fileobj.close()


class XMLPrefReader(handler.ContentHandler):
    """Handler for xml file reading"""

    def __init__(self, pref=None):
        handler.ContentHandler.__init__(self)
        self.key = None
        self.value = None
        self.pref = pref

    def startElement(self, name, attrs):
        self.key = name

    def endElement(self, name):
        if name != 'preferences':
            try:
                line = path_system('self.value=' + self.value)
                code = compile(line, '<string>', 'exec')
                exec code
                self.pref.__dict__[self.key] = self.value
            except Exception as e:
                LOG.error('Error in "%s" %s', line, e)

    def characters(self, data):
        self.value = data


class ErrorHandler(handler.ErrorHandler):
    pass


class EntityResolver(handler.EntityResolver):
    pass


class DTDHandler(handler.DTDHandler):
    pass
