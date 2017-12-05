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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import sys
import os

import uc2
from uc2 import _, cms, uc2const
from uc2 import events, msgconst
from uc2.uc_conf import UCData, UCConfig
from uc2.formats import get_loader, get_saver
from uc2.app_palettes import PaletteManager

HELP_TEMPLATE = '''
%s

USAGE: uniconvertor [OPTIONS] [INPUT FILE] [OUTPUT FILE]

Universal vector graphics format translator.
sK1 Team (http://www.sk1project.net), copyright (C) 2007-%s by Igor E. Novikov

 Supported input vector graphics file formats:
   %s

 Supported input palette file formats:
   %s

 Supported input image file formats:
   %s

-------------------------------------------------------------------------------
 Supported output vector graphics file formats:
   %s

 Supported output palette file formats:
   %s

 Supported output image file formats:
   %s

Example: uniconvertor drawing.cdr drawing.svg

 Available options:
 --help    Show this help
 -verbose  Internal logs printed while translation
'''


class UCApplication(object):
    path = ''
    config = None
    appdata = None
    default_cms = None
    palettes = None

    def __init__(self, path='', cfgdir='~'):
        self.path = path
        self.config = UCConfig()
        self.config.app = self
        self.appdata = UCData(self, cfgdir)
        setattr(uc2, "config", self.config)
        setattr(uc2, "appdata", self.appdata)

    def _get_infos(self, loaders):
        return '\n   '.join(
            [uc2const.FORMAT_DESCRIPTION[loader] for loader in loaders])

    def show_help(self):
        app_name = '%s %s%s' % (
            self.appdata.app_name, self.appdata.version, self.appdata.revision)
        print HELP_TEMPLATE % (app_name, str(datetime.date.today().year),
                               self._get_infos(uc2const.MODEL_LOADERS),
                               self._get_infos(uc2const.PALETTE_LOADERS),
                               self._get_infos(uc2const.BITMAP_LOADERS),
                               self._get_infos(uc2const.MODEL_SAVERS),
                               self._get_infos(uc2const.PALETTE_SAVERS),
                               self._get_infos(uc2const.BITMAP_SAVERS),)
        sys.exit(0)

    def verbose(self, *args):
        args, = args
        status = msgconst.MESSAGES[args[0]]
        ident = ' ' * (msgconst.MAX_LEN - len(status))
        print '%s%s| %s' % (status, ident, args[1])

    def run(self):

        if len(sys.argv) < 3 or '--help' in sys.argv:
            self.show_help()

        files = []
        options_list = []
        options = {}

        for item in sys.argv[1:]:
            if item[0] == '-':
                if item == '-verbose':
                    events.connect(events.MESSAGES, self.verbose)
                else:
                    options_list.append(item)
            else:
                files.append(item)

        if len(files) != 2:
            self.show_help()
        if not os.path.lexists(files[0]):
            self.show_help()

        for item in options_list:
            result = item[1:].split('=')
            if not len(result) == 2:
                continue
            else:
                key, value = result
                if value == 'yes':
                    value = True
                if value == 'no':
                    value = False
                options[key] = value

        self.default_cms = cms.ColorManager()
        self.palettes = PaletteManager(self)

        print ''
        msg = _('Translation of') + ' "%s" ' % (files[0]) + _('into "%s"') % (
            files[1])
        events.emit(events.MESSAGES, msgconst.JOB, msg)

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

            print '\n', sys.exc_info()[1], sys.exc_info()[2]
            sys.exit(1)

        if doc is not None:
            try:
                saver(doc, files[1])
            except Exception:
                msg = _("Error while translation and saving '%s'") % (files[0])
                events.emit(events.MESSAGES, msgconst.ERROR, msg)

                msg = _('Translation is interrupted')
                events.emit(events.MESSAGES, msgconst.STOP, msg)

                print '\n', sys.exc_info()[1], sys.exc_info()[2]
                sys.exit(1)
        else:
            msg = _("Error while model creating for '%s'") % (files[0])
            events.emit(events.MESSAGES, msgconst.ERROR, msg)

            msg = _('Translation is interrupted')
            events.emit(events.MESSAGES, msgconst.STOP, msg)
            sys.exit(1)

        doc.close()
        events.emit(events.MESSAGES, msgconst.OK,
                    _('Translation is successful'))
        print ''

        sys.exit(0)
