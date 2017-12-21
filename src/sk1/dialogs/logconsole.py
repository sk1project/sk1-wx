# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017 by Igor E. Novikov
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

import os
import wal

from sk1 import _, config
from sk1.dialogs import filedlgs
from sk1.resources import icons
from uc2 import uc2const
from uc2.utils.fsutils import get_fileptr

FUCSIA = (144, 84, 141)
YELLOW = (217, 175, 106)
RED = (170, 73, 38)
BLUE = (81, 124, 194)
DARK = (122, 122, 122)
LIGHT = (170, 181, 189)

COLOR_MAP = {
    'ERROR': RED,
    'WARNING': YELLOW,
    'DEBUG': DARK,
    'INFO': LIGHT,
}

FG_COLOR = LIGHT
BG_COLOR = (43, 43, 43)


class ConsoleDialog(wal.SimpleDialog):
    presenter = None
    entry = None
    lpanel = None
    log_path = None
    zoom = 0

    def __init__(self, parent, title):
        self.app = parent.app
        self.title = title
        self.zoom = config.console_dlg_zoom
        size = config.console_dlg_size
        wal.SimpleDialog.__init__(self, parent, title, size,
                                  style=wal.VERTICAL, resizable=True,
                                  add_line=False, margin=0)
        self.set_minsize(config.console_dlg_minsize)

    def build(self):
        self.toolbar = ConsoleToolbar(self, self)
        self.pack(self.toolbar, fill=True)
        hpanel = wal.HPanel(self)
        self.pack(hpanel, fill=True, expand=True)
        self.lpanel = wal.VPanel(hpanel)
        self.lpanel.set_bg((49, 51, 53))
        self.lpanel.pack((26, 26))
        hpanel.pack(self.lpanel, fill=True)
        hpanel.pack(wal.PLine(hpanel, (85, 85, 85)), fill=True)
        self.entry = wal.Entry(hpanel, '', multiline=True, editable=False,
                               richtext=True, no_border=True)
        self.entry.set_bg(BG_COLOR)
        hpanel.pack(self.entry, fill=True, expand=True)
        self.log_path = os.path.join(self.app.appdata.app_config_dir, 'sk1.log')
        self.load_logs(self.log_path)

    def zoom_in(self):
        self.zoom = self.zoom + 1 if self.zoom < 7 else self.zoom
        self.load_logs(self.log_path)

    def zoom_out(self):
        self.zoom = self.zoom - 1 if self.zoom > -3 else self.zoom
        self.load_logs(self.log_path)

    def load_logs(self, log_path):
        if not os.path.lexists(log_path):
            return
        fileptr = get_fileptr(log_path)
        self.entry.clear()
        self.entry.set_monospace(self.zoom)
        while True:
            line = fileptr.readline()
            if not line:
                break
            color = COLOR_MAP.get(line[:9].strip(), None)
            if not color:
                for item in COLOR_MAP:
                    if item in line:
                        color = COLOR_MAP[item]
                        break
            color = color or DARK
            self.entry.set_text_colors(color)
            self.entry.append(line)
        self.set_title('%s - [%s]' % (self.title, log_path))

    def open_log(self):
        log_file = filedlgs.get_open_file_name(self, config.log_dir,
                                               _('Select log to open'),
                                               file_types=[uc2const.LOG, ])
        print log_file

    def save_as_log(self):
        path = os.path.join(config.log_dir, 'sk1.log')
        log_file = filedlgs.get_save_file_name(self, path,
                                               _('Save log As...'),
                                               file_types=[uc2const.LOG, ])
        print log_file

    def show(self):
        self.show_modal()
        w, h = self.get_size()
        if wal.IS_UNITY_16:
            h = max(h - 28, config.console_dlg_minsize[1])
        config.console_dlg_size = (w, h)
        config.console_dlg_zoom = self.zoom
        self.destroy()


class ConsoleToolbar(wal.HPanel):

    def __init__(self, parent, dlg):
        self.dlg = dlg
        wal.HPanel.__init__(self, parent)

        Btn = wal.ImageButton

        buttons = [
            (icons.PD_OPEN, self.dlg.open_log, _('Open log file...')),
            (icons.PD_FILE_SAVE_AS, self.dlg.save_as_log, _('Save logs as...')),
            None,
            (icons.PD_ZOOM_IN, self.dlg.zoom_in, _('Zoom in')),
            (icons.PD_ZOOM_OUT, self.dlg.zoom_out, _('Zoom out')),
            None,
            (icons.PD_PREFERENCES, self.stub, _('Viewer preferences')),
        ]

        for item in buttons:
            if item:
                self.pack(Btn(self, item[0], wal.SIZE_22,
                              tooltip=item[2], onclick=item[1]))
            elif item is None:
                self.pack(wal.VLine(self), padding_all=5, fill=True)
            else:
                self.pack((5, 5), expand=True)

    def stub(self):
        pass


def logconsole_dlg(parent, title='Logs'):
    dlg = ConsoleDialog(parent, title)
    return dlg.show()
