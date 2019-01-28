# -*- coding: utf-8 -*-
#
#  Copyright (C) 2012-2017 by Igor E. Novikov
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

import datetime
import logging
import os
import sys

import uc2
from uc2 import app_cms, uc2const
from uc2 import events, msgconst
from uc2.app_palettes import PaletteManager
from uc2.formats import get_loader, get_saver, get_saver_by_id
from uc2.uc2conf import UCData, UCConfig
from uc2.utils import fsutils
from uc2.utils.mixutils import echo, config_logging

LOG = logging.getLogger(__name__)


def log_stub(*args):
    return args


LOG_MAP = {
    msgconst.JOB: LOG.info,
    msgconst.INFO: LOG.info,
    msgconst.OK: LOG.info,
    msgconst.WARNING: LOG.warn,
    msgconst.ERROR: LOG.error,
    msgconst.STOP: log_stub,
}

HELP_TEMPLATE = '''
%s

Universal vector graphics format translator
copyright (C) 2007-%s sK1 Project Team (https://sk1project.net)

Usage: uniconvertor [OPTIONS] [INPUT FILE] [OUTPUT FILE]
Example: uniconvertor drawing.cdr drawing.svg

 Available options:
 --help      Display this help and exit
 --verbose   Show internal logs
 --log=      Logging level: DEBUG, INFO, WARN, ERROR (by default, INFO)
 --format=   Type of output file format (values provided below)

---INPUT FILE FORMATS-------------------------------

 Supported input vector graphics file formats:
   %s

 Supported input palette file formats:
   %s

 Supported input image file formats:
   %s

---OUTPUT FILE FORMATS------------------------------

 Supported output vector graphics file formats:
   %s

 Supported output palette file formats:
   %s

 Supported output image file formats:
   %s

----------------------------------------------------
'''


class UCApplication(object):
    path = ''
    config = None
    appdata = None
    default_cms = None
    palettes = None
    do_verbose = False
    log_filepath = ''

    def __init__(self, path='', cfgdir='~', check=True):
        self.path = path
        cfgdir = fsutils.expanduser(fsutils.get_utf8_path(cfgdir))
        self.config = UCConfig()
        self.config.app = self
        self.appdata = UCData(self, cfgdir, check=check)
        setattr(uc2, 'config', self.config)
        setattr(uc2, 'appdata', self.appdata)

    def _get_infos(self, loaders):
        result = []
        for loader in loaders:
            if loader in (uc2const.COREL_PAL, uc2const.SCRIBUS_PAL):
                desc = uc2const.FORMAT_DESCRIPTION[loader]
                desc = desc.replace(' - ', ') - ')
                result.append('%s (%s' % (uc2const.FORMAT_NAMES[loader], desc))
            else:
                result.append(uc2const.FORMAT_DESCRIPTION[loader])
        return '\n   '.join(result)

    def show_help(self):
        mark = '' if not self.appdata.build \
            else ' build %s' % self.appdata.build
        app_name = '%s %s%s%s' % (self.appdata.app_name, self.appdata.version,
                                  self.appdata.revision, mark)
        echo(HELP_TEMPLATE % (app_name, str(datetime.date.today().year),
                              self._get_infos(uc2const.MODEL_LOADERS),
                              self._get_infos(uc2const.PALETTE_LOADERS),
                              self._get_infos(uc2const.BITMAP_LOADERS),
                              self._get_infos(uc2const.MODEL_SAVERS),
                              self._get_infos(uc2const.PALETTE_SAVERS),
                              self._get_infos(uc2const.BITMAP_SAVERS),))
        sys.exit(0)

    def show_short_help(self, msg):
        echo('')
        echo(msg)
        echo('USAGE: uniconvertor [OPTIONS] [INPUT FILE] [OUTPUT FILE]')
        echo('Use --help for more details.' + '\n')
        sys.exit(1)

    def verbose(self, *args):
        status = msgconst.MESSAGES[args[0]]
        LOG_MAP[args[0]](args[1])
        if self.do_verbose or args[0] in (msgconst.ERROR, msgconst.STOP):
            indent = ' ' * (msgconst.MAX_LEN - len(status))
            echo('%s%s| %s' % (status, indent, args[1]))
        if args[0] == msgconst.STOP:
            echo('For details see logs: %s\n' % self.log_filepath)
            sys.exit(1)

    def run(self, cwd=None):
        if '--help' in sys.argv or '-help' in sys.argv or len(sys.argv) == 1:
            self.show_help()
        elif len(sys.argv) == 2:
            self.show_short_help('Not enough arguments!')

        files = []
        options_list = []
        options = {}

        for item in sys.argv[1:]:
            if item.startswith('--'):
                options_list.append(item)
            elif item.startswith('-'):
                self.show_short_help('Unknown option "%s"' % item)
            else:
                filename = fsutils.get_utf8_path(item)
                if not os.path.dirname(filename) and cwd:
                    filename = os.path.join(cwd, filename)
                files.append(filename)

        if not files:
            self.show_short_help('File names are not provided!')
        elif len(files) == 1:
            self.show_short_help('Destination file name is not provided!')
        elif not os.path.lexists(files[0]):
            self.show_short_help('Source file "%s" is not found!' % files[0])

        for item in options_list:
            result = item[2:].split('=')
            if not len(result) == 2:
                options[result[0]] = True
            else:
                key, value = result
                value = value.replace('"', '').replace("'", '')
                if value.isdigit():
                    value = int(value)
                elif value.replace('.', '').isdigit():
                    value = float(value)
                elif value.lower() in ('yes', 'no'):
                    value = {'yes': True, 'no': False}[value.lower()]
                options[key] = value

        self.do_verbose = options.get('verbose', False)
        events.connect(events.MESSAGES, self.verbose)
        log_level = options.get('log', self.config.log_level)
        self.log_filepath = os.path.join(self.appdata.app_config_dir, 'uc2.log')
        config_logging(self.log_filepath, log_level)

        self.default_cms = app_cms.AppColorManager(self)
        self.palettes = PaletteManager(self)

        msg = 'Translation of "%s" into "%s"' % (files[0], files[1])
        events.emit(events.MESSAGES, msgconst.JOB, msg)

        saver_ids = uc2const.PALETTE_SAVERS
        saver_ids += uc2const.MODEL_SAVERS + uc2const.BITMAP_SAVERS
        sid = options.get('format', '').lower()
        if sid and sid in saver_ids:
            saver_id = sid
            saver = get_saver_by_id(saver_id)
        else:
            saver, saver_id = get_saver(files[1], return_id=True)
        if saver is None:
            msg = 'Output file format of "%s" is unsupported.' % files[1]
            events.emit(events.MESSAGES, msgconst.ERROR, msg)

            msg = 'Translation is interrupted'
            events.emit(events.MESSAGES, msgconst.STOP, msg)

        loader, loader_id = get_loader(files[0], return_id=True)
        if loader is None:
            msg = 'Input file format of "%s" is unsupported.' % files[0]
            events.emit(events.MESSAGES, msgconst.ERROR, msg)

            msg = 'Translation is interrupted'
            events.emit(events.MESSAGES, msgconst.STOP, msg)

        doc = None
        try:
            if loader_id in uc2const.PALETTE_LOADERS and \
                    saver_id in uc2const.PALETTE_SAVERS:
                doc = loader(self.appdata, files[0], convert=True, **options)
            else:
                doc = loader(self.appdata, files[0], **options)
        except Exception as e:
            msg = 'Error while loading "%s"' % files[0]
            msg += 'The file may be corrupted or contains unknown file format.'
            events.emit(events.MESSAGES, msgconst.ERROR, msg)

            msg = 'Loading is interrupted'
            LOG.error('%s %s', msg, e)
            events.emit(events.MESSAGES, msgconst.STOP, msg)

        if doc is not None:
            try:
                if loader_id in uc2const.PALETTE_LOADERS and \
                        saver_id in uc2const.PALETTE_SAVERS:
                    saver(doc, files[1], translate=False, convert=True,
                          **options)
                else:
                    saver(doc, files[1], **options)
            except Exception as e:
                msg = 'Error while translation and saving "%s"' % files[0]
                events.emit(events.MESSAGES, msgconst.ERROR, msg)

                msg = 'Translation is interrupted'
                LOG.error('%s %s', msg, e, exc_info=True)
                events.emit(events.MESSAGES, msgconst.STOP, msg)
        else:
            msg = 'Error creating model for "%s"' % files[0]
            events.emit(events.MESSAGES, msgconst.ERROR, msg)

            msg = 'Translation is interrupted'
            events.emit(events.MESSAGES, msgconst.STOP, msg)

        doc.close()
        msg = 'Translation is successful'
        events.emit(events.MESSAGES, msgconst.OK, msg)
        if self.do_verbose:
            echo('')

        sys.exit(0)
