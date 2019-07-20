# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2015 by Igor E. Novikov
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

import sys
import wal

from sk1 import _, events, config
from sk1.dialogs.aboutdlg_credits import CREDITS
from sk1.dialogs.aboutdlg_license import LICENSE
from sk1.resources import icons, get_bmp
from uc2 import uc2const


class AboutDialog(wal.SimpleDialog):
    sizer = None
    app = None

    def __init__(self, app, parent, title, size=config.about_dlg_size):
        self.app = app
        wal.SimpleDialog.__init__(self, parent, title, size, margin=0,
                                  resizable=False, add_line=False)

    def build(self):
        nb = wal.Notebook(self)
        nb.add_page(AboutPage(self.app, nb), _('About'))
        nb.add_page(ComponentsPage(nb), _('Components'))
        nb.add_page(TranslatorsPage(nb), _('Translators'))
        nb.add_page(ThanksPage(nb), _('Thanks to'))
        nb.add_page(LicensePage(nb), _('License'))
        self.pack(nb, expand=True, fill=True, padding_all=5)


class AboutPage(wal.HPanel):
    def __init__(self, app, parent):
        wal.HPanel.__init__(self, parent)
        hp = wal.HPanel(self)
        self.pack(hp)
        hp.pack((55, 15))
        logo_p = wal.VPanel(hp)
        hp.pack(logo_p, fill=True)
        logo_p.pack(get_bmp(logo_p, icons.SK1_ICON48), padding=5)
        hp.pack((10, 5))

        box = wal.VPanel(hp)
        hp.pack(box, padding=5)
        data = app.appdata
        txt = data.app_name + ' - ' + _('vector graphics editor')
        box.pack(wal.Label(box, txt, True, 2), fill=True)

        data = app.appdata
        mark = '' if not data.build else ' %s %s' % (_('build'), data.build)
        txt = '%s: %s %s%s' % (_('Version'), data.version, data.revision, mark)
        box.pack(wal.Label(box, txt), fill=True)
        box.pack((35, 35))

        import datetime
        year = str(datetime.date.today().year)
        txt = '(C) 2011-%s sK1 Project team' % year + '\n'
        box.pack(wal.Label(box, txt), fill=True)
        p = wal.HPanel(box)
        p.pack(wal.HtmlLabel(p, 'https://sk1project.net'))
        box.pack(p, fill=True)


class ComponentsPage(wal.VPanel):
    def __init__(self, parent):
        wal.VPanel.__init__(self, parent)
        from uc2 import libimg, libpango, libcairo, cms
        import reportlab

        data = [[_('Component'), _('Version')]]
        mark = '' if not uc2const.BUILD else ' build %s' % uc2const.BUILD
        uc_ver = '%s %s%s' % (uc2const.VERSION, uc2const.REVISION, mark)
        data.append(['Python', sys.version])
        data.append(['wxWidgets', wal.VERSION])
        data.append(['UniConvertor', uc_ver])
        data.append(['LCMS', cms.libcms.get_version()])
        data.append(['Cairo', libcairo.get_version()[0]])
        data.append(['pycairo', libcairo.get_version()[1]])
        data.append(['Pillow', libimg.get_version()])
        data.append(['ImageMagick', libimg.get_magickwand_version()[0]])
        data.append(['Pango', libpango.get_version()])
        data.append(['Reportlab', reportlab.Version])

        if not wal.IS_MSW:
            import cups
            try:
                cups.require('10.0')
            except RuntimeError as e:
                data.append(['pycups', str(e).split()[-1]])

        slist = wal.ReportList(self, data, border=False)
        self.pack(slist, expand=True, fill=True, padding=5)
        slist.set_column_width(0, wal.LIST_AUTOSIZE)


TR_LIST = [
    ['LANG', 'Translators'],
    ['Brazilian Portuguese','João Lima Neto <contato@joaolimaneto.com.br>'],
    ['German', 'Thore Sommer <mail@thson.de>'],
    ['Russian', 'Igor Novikov <sk1.project.org@gmail.com>'],
    ['Spanish', 'Carlos Jesús Atagua Díaz <atacarlos@gmail.com>'],
    ['Ukrainian', 'Maxim Barabash <maxim.s.barabash@gmail.com>,'],
    ['',          'Eugeniy Fedirets <evgeniy_fedirets@ukr.net>'],
]


class TranslatorsPage(wal.VPanel):
    def __init__(self, parent):
        wal.VPanel.__init__(self, parent)
        tr_list = wal.ReportList(self, TR_LIST, border=False)
        self.pack(tr_list, expand=True, fill=True, padding=5)
        tr_list.set_column_width(0, wal.LIST_AUTOSIZE)


class ThanksPage(wal.VPanel):
    def __init__(self, parent):
        wal.VPanel.__init__(self, parent)
        entry = wal.Entry(self, CREDITS, multiline=True, editable=False)
        self.pack(entry, expand=True, fill=True, padding=5)


class LicensePage(wal.VPanel):
    def __init__(self, parent):
        wal.VPanel.__init__(self, parent)
        entry = wal.Entry(self, LICENSE, multiline=True, editable=False)
        self.pack(entry, expand=True, fill=True, padding=5)


class EvetLoopMonitor(wal.VPanel):
    def __init__(self, parent):
        wal.VPanel.__init__(self, parent)
        data = [['EventLoop', 'Connections']]
        for item in events.ALL_CHANNELS:
            data.append([item[0], str(len(item) - 1)])
        slist = wal.ReportList(self, data, border=False)
        self.pack(slist, expand=True, fill=True)
        slist.set_column_width(0, wal.LIST_AUTOSIZE)


def about_dialog(app, parent):
    title = _('About') + ' ' + app.appdata.app_name
    dlg = AboutDialog(app, parent, title)
    dlg.Refresh()
    dlg.show()
