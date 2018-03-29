# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013 by Igor E. Novikov
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

import wal
from sk1 import config
from sk1.resources import pdids

BUTTONS = [
    (wal.ID_NEW,), None,
    (wal.ID_OPEN, wal.ID_SAVE, wal.ID_SAVEAS, wal.ID_CLOSE), None,
    (wal.ID_PRINT,), None,
    (wal.ID_UNDO, wal.ID_REDO), None,
    (wal.ID_CUT, wal.ID_COPY, wal.ID_PASTE, wal.ID_DELETE), None,
    (wal.ID_REFRESH,), None,
    (wal.ID_ZOOM_IN, wal.ID_ZOOM_OUT, pdids.ID_ZOOM_PAGE, wal.ID_ZOOM_100,
     wal.ID_ZOOM_FIT), None,
    (wal.ID_PROPERTIES, wal.ID_PREFERENCES)
]


def build_toolbar(mw):
    tb = mw.CreateToolBar(wal.TBFLAGS)
    icon_size = config.toolbar_icon_size
    tb.SetToolBitmapSize(config.toolbar_size)

    for items in BUTTONS:
        if items is None:
            tb.AddSeparator()
        else:
            for item in items:
                action = mw.app.actions[item]
                aid = action.action_id
                label_txt = wal.tr(action.get_tooltip_text())
                hlp_txt = wal.tr(action.get_descr_text())
                bmp = action.get_icon(icon_size, wal.ART_TOOLBAR)
                if not bmp:
                    continue
                if wal.IS_MSW:
                    tb.AddLabelTool(aid, label_txt, bmp,
                                    bmpDisabled=wal.disabled_bmp(bmp),
                                    shortHelp=hlp_txt)
                else:
                    tb.AddLabelTool(aid, label_txt, bmp,
                                    shortHelp=hlp_txt)
                action.register_as_tool(tb)
    tb.Realize()
    return tb
