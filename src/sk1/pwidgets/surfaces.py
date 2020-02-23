# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Ihor E. Novikov
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

import wal

from sk1 import events, config
from sk1.appconst import RENDERING_DELAY
from uc2 import uc2const
from uc2.uc2const import point_dict

from .canvas_menu import CanvasCtxMenu
from .kbd_proc import KbdProcessor


class Painter(object):

    def destroy(self):
        items = self.__dict__.keys()
        for item in items:
            self.__dict__[item] = None

    def check_config(self, *args):
        pass

    def paint(self):
        pass

    def mouse_left_down(self, point):
        pass

    def mouse_left_up(self, point):
        pass

    def mouse_move(self, point):
        pass


class RulerSurface(wal.RulerCanvas):
    def __init__(self, app, parent):
        self.app = app
        wal.RulerCanvas.__init__(self, parent, config.ruler_size)
        events.connect(events.CONFIG_MODIFIED, self.check_config)

    @property
    def painter(self):
        if self.app.current_doc:
            return self.app.current_doc.corner

    def check_config(self, *args):
        if args[0].startswith('ruler_'):
            self.painter.check_config(*args)
            if args[0] == 'ruler_size':
                self.fix_size(config.ruler_size)
            self.refresh()

    def paint(self):
        if self.painter:
            self.painter.paint()

    def mouse_left_down(self, point):
        if self.painter:
            self.painter.mouse_left_down(point)

    def mouse_left_up(self, point):
        if self.painter:
            self.painter.mouse_left_up(point)

    def mouse_move(self, point):
        if self.painter:
            self.painter.mouse_move(point)


class HRulerSurface(RulerSurface):
    @property
    def painter(self):
        if self.app.current_doc:
            return self.app.current_doc.hruler


class VRulerSurface(HRulerSurface):
    @property
    def painter(self):
        if self.app.current_doc:
            return self.app.current_doc.vruler


class CanvasEvent(wal.MouseEvent):
    def get_rotation(self):
        return wal.MouseEvent.get_rotation(
            self) / config.mouse_scroll_sensitivity


class CanvasSurface(wal.MainCanvas):
    hscroll = None
    vscroll = None
    my_changes = False
    redraw_flag = False
    request_redraw_flag = False

    def __init__(self, app, parent):
        self.app = app
        wal.MainCanvas.__init__(self, parent, rendering_delay=RENDERING_DELAY)
        self.ctx_menu = CanvasCtxMenu(self.app, self)
        self.kbproc = KbdProcessor(self.app)
        self.set_drop_target(wal.FileDropHandler(self, self.drop_file))

    @property
    def painter(self):
        if self.app.current_doc:
            return self.app.current_doc.canvas

    def show_context_menu(self):
        self.ctx_menu.rebuild()
        self.PopupMenu(self.ctx_menu)

    def force_redraw(self):
        if self.redraw_flag:
            self.request_redraw_flag = True
        else:
            self.redraw_flag = True
            self.refresh(clear=False)

    def drop_file(self, x, y, filename):
        self.app.import_file(filename, [x, y])

    # ==============SCROLLING==========================

    def set_scrolls(self, hscroll, vscroll):
        self.hscroll = hscroll
        self.vscroll = vscroll
        self.hscroll.set_scrollbar(500, 100, 1100, 100, refresh=True)
        self.vscroll.set_scrollbar(500, 100, 1100, 100, refresh=True)
        self.hscroll.set_callback(self._scrolling)
        self.vscroll.set_callback(self._scrolling)

    def _scrolling(self):
        if self.my_changes:
            return
        xpos = self.hscroll.get_thumb_pos() / 1000.0
        ypos = (1000 - self.vscroll.get_thumb_pos()) / 1000.0
        x = (xpos - 0.5) * self.painter.workspace[0]
        y = (ypos - 0.5) * self.painter.workspace[1]
        center = self.painter.doc_to_win([x, y])
        self.painter._set_center(center)
        self.force_redraw()

    def update_scrolls(self):
        if self.painter:
            self.my_changes = True
            center = self.painter._get_center()
            workspace = self.painter.workspace
            x = (center[0] + workspace[0] / 2.0) / workspace[0]
            y = (center[1] + workspace[1] / 2.0) / workspace[1]
            hscroll = int(1000 * x)
            vscroll = int(1000 - 1000 * y)
            self.hscroll.set_scrollbar(hscroll, 100, 1100, 100, refresh=True)
            self.vscroll.set_scrollbar(vscroll, 100, 1100, 100, refresh=True)
            self.my_changes = False

    # ==============EVENT CONTROLLING==========================

    def paint(self):
        if self.painter:
            self.painter.paint()
            self.redraw_flag = False
            if self.request_redraw_flag:
                self.request_redraw_flag = False
                self.force_redraw()

    def on_timer(self):
        if self.painter:
            self.painter.controller.on_timer()

    def mouse_left_down(self, event):
        if self.painter:
            self.painter.controller.set_cursor()
            self.painter.controller.mouse_down(CanvasEvent(event))

    def mouse_left_up(self, event):
        if self.painter:
            self.painter.controller.mouse_up(CanvasEvent(event))

    def mouse_left_dclick(self, event):
        if self.painter:
            self.painter.controller.set_cursor()
            self.painter.controller.mouse_double_click(CanvasEvent(event))

    def mouse_move(self, event):
        if self.painter:
            event = CanvasEvent(event)
            x, y = self.painter.win_to_doc_coords(event.get_point())
            unit = self.painter.presenter.model.doc_units
            tr_unit = uc2const.unit_short_names[unit]
            msg = '  %i x %i' % (x * point_dict[unit], y * point_dict[unit])
            events.emit(events.MOUSE_STATUS, '%s %s' % (msg, tr_unit))
            self.painter.controller.mouse_move(event)

    def mouse_right_down(self, event):
        if self.painter:
            self.painter.controller.mouse_right_down(CanvasEvent(event))

    def mouse_right_up(self, event):
        if self.painter:
            self.painter.controller.mouse_right_up(CanvasEvent(event))

    def mouse_middle_down(self, event):
        if self.painter:
            self.painter.controller.mouse_middle_down(CanvasEvent(event))

    def mouse_middle_up(self, event):
        if self.painter:
            self.painter.controller.mouse_middle_up(CanvasEvent(event))

    def mouse_wheel(self, event):
        if self.painter:
            self.painter.controller.wheel(CanvasEvent(event))
