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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import logging
import os
import sys

import uc2
from uc2 import _, cms, uc2const
from uc2 import events, msgconst
from uc2.app_palettes import PaletteManager
from uc2.formats import get_loader, get_saver, get_saver_by_id
from uc2.uc2conf import UCData, UCConfig
from uc2.utils.mixutils import echo, config_logging

LOG = logging.getLogger(__name__)

LOG_MAP = {
    msgconst.JOB: LOG.info,
    msgconst.INFO: LOG.info,
    msgconst.OK: LOG.info,
    msgconst.WARNING: LOG.warn,
    msgconst.ERROR: LOG.error,
    msgconst.STOP: LOG.error,
}

HELP_TEMPLATE = '''
%s

Universal vector graphics format translator
sK1 Team (http://www.sk1project.net), copyright (C) 2007-%s by Igor E. Novikov

USAGE: uniconvertor [OPTIONS] [INPUT FILE] [OUTPUT FILE]
Example: uniconvertor drawing.cdr drawing.svg

 Available options:
 --help      Show this help
 --verbose   Internal logs printed while translation
 --log=      Logging level: DEBUG, INFO, WARN, ERRROR (default INFO)
 --format=   Type of output file format

----------------------------------------------------

 Supported input vector graphics file formats:
   %s

 Supported input palette file formats:
   %s

 Supported input image file formats:
   %s

----------------------------------------------------

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

    def __init__(self, path='', cfgdir='~'):
        self.path = path
        self.config = UCConfig()
        self.config.app = self
        self.appdata = UCData(self, cfgdir)
        setattr(uc2, "config", self.config)
        setattr(uc2, "appdata", self.appdata)

    def _get_infos(self, loaders):
        result = []
        for loader in loaders:
            if loader in (uc2const.COREL_PAL, uc2const.SCRIBUS_PAL):
                descr = uc2const.FORMAT_DESCRIPTION[loader]
                descr = descr.replace(' - ', ') - ')
                result.append('%s (%s' % (loader.upper(), descr))
            else:
                result.append(uc2const.FORMAT_DESCRIPTION[loader])
        return '\n   '.join(result)

    def show_help(self):
        app_name = '%s %s%s' % (
            self.appdata.app_name, self.appdata.version, self.appdata.revision)
        echo(HELP_TEMPLATE % (app_name, str(datetime.date.today().year),
                              self._get_infos(uc2const.MODEL_LOADERS),
                              self._get_infos(uc2const.PALETTE_LOADERS),
                              self._get_infos(uc2const.BITMAP_LOADERS),
                              self._get_infos(uc2const.MODEL_SAVERS),
                              self._get_infos(uc2const.PALETTE_SAVERS),
                              self._get_infos(uc2const.BITMAP_SAVERS),))
        sys.exit(0)

    def show_short_help(self, msg):
        echo(msg)
        echo('USAGE: uniconvertor [OPTIONS] [INPUT FILE] [OUTPUT FILE]')
        echo('Use --help for more details.')
        sys.exit(1)

    def verbose(self, *args):
        status = msgconst.MESSAGES[args[0]]
        LOG_MAP[args[0]](args[1])
        if self.do_verbose:
            ident = ' ' * (msgconst.MAX_LEN - len(status))
            echo('%s%s| %s' % (status, ident, args[1]))

    def run(self):

        if '--help' in sys.argv or '-help' in sys.argv:
            self.show_help()
        elif len(sys.argv) < 3:
            self.show_short_help('Not enough arguments!')

        files = []
        options_list = []
        options = {}

        for item in sys.argv[1:]:
            if item.startswith('--'):
                options_list.append(item)
            elif item.startswith('-'):
                self.show_short_help('Unknown option %s' % item)
            else:
                files.append(item)

        if not file:
            self.show_short_help('File names are not provided!')
        elif len(files) == 1:
            self.show_short_help('Destination file name is not provided!')
        elif not os.path.lexists(files[0]):
            self.show_short_help('Source file % is not found!' % files[0])

        for item in options_list:
            result = item[2:].split('=')
            if not len(result) == 2:
                options[result[0]] = True
            else:
                key, value = result
                value = value.replace('"', '').replace("'", '')
                if value == 'yes':
                    value = True
                if value == 'no':
                    value = False
                options[key] = value

        self.do_verbose = options.get('verbose', False)
        events.connect(events.MESSAGES, self.verbose)
        log_level = options.get('log', self.config.log_level)
        filepath = os.path.join(self.appdata.app_config_dir, 'uc2.log')
        config_logging(filepath, log_level)

        self.default_cms = cms.ColorManager()
        self.palettes = PaletteManager(self)

        echo('')
        msg = _('Translation of') + ' "%s" ' % (files[0]) + _('into "%s"') % (
            files[1])
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
            msg = _("Output file format of '%s' is unsupported.") % (files[1])
            events.emit(events.MESSAGES, msgconst.ERROR, msg)

            msg = _('Translation is interrupted')
            events.emit(events.MESSAGES, msgconst.STOP, msg)

            sys.exit(1)

        loader, loader_id = get_loader(files[0], return_id=True)
        if loader is None:
            msg = _("Input file format of '%s' is unsupported.") % (files[0])
            events.emit(events.MESSAGES, msgconst.ERROR, msg)

            msg = _('Translation is interrupted')
            events.emit(events.MESSAGES, msgconst.STOP, msg)

            sys.exit(1)

        try:
            if loader_id in uc2const.PALETTE_LOADERS and \
                    saver_id in uc2const.PALETTE_SAVERS:
                doc = loader(self.appdata, files[0], convert=True)
            else:
                doc = loader(self.appdata, files[0])
        except Exception:
            msg = _("Error while loading '%s'") % (files[0])
            msg += _(
                "The file may be corrupted or contains unknown file format.")
            events.emit(events.MESSAGES, msgconst.ERROR, msg)

            msg = _('Translation is interrupted')
            events.emit(events.MESSAGES, msgconst.STOP, msg)

            echo('\n' + sys.exc_info()[1] + '\n' + sys.exc_info()[2])
            sys.exit(1)

        if doc is not None:
            try:
                if loader_id in uc2const.PALETTE_LOADERS and \
                        saver_id in uc2const.PALETTE_SAVERS:
                    saver(doc, files[1], translate=False, convert=True)
                else:
                    saver(doc, files[1])
            except Exception:
                msg = _("Error while translation and saving '%s'") % (files[0])
                events.emit(events.MESSAGES, msgconst.ERROR, msg)

                msg = _('Translation is interrupted')
                events.emit(events.MESSAGES, msgconst.STOP, msg)

                echo('\n' + sys.exc_info()[1] + '\n' + sys.exc_info()[2])
                sys.exit(1)
        else:
            msg = _("Error while model creating for '%s'") % (files[0])
            events.emit(events.MESSAGES, msgconst.ERROR, msg)

            msg = _('Translation is interrupted')
            events.emit(events.MESSAGES, msgconst.STOP, msg)
            sys.exit(1)

        doc.close()
        msg = _('Translation is successful')
        events.emit(events.MESSAGES, msgconst.OK, msg)
        echo('')

        sys.exit(0)
