# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013 by Ihor E. Novikov
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

from copy import deepcopy

from sk1 import _, events, config
from sk1.pwidgets import UnitSpin, ActionButton, ActionToggle
from sk1.resources import icons, get_bmp, pdids
from uc2.uc2const import ORIENTS_NAMES, PAGE_FORMATS_MORE
from uc2.uc2const import PAGE_FORMATS, PAGE_FORMAT_NAMES, PORTRAIT, LANDSCAPE
from wal import Combolist, LEFT, CENTER, ImageToggleButton
from wal import VLine, ALL, EXPAND

from .base import CtxPlugin


class PagePlugin(CtxPlugin):
    name = 'PagePlugin'
    update_flag = False
    format = None
    formats = None
    combo = None
    width_spin = None
    height_spin = None
    portrait = None
    landscape = None

    def __init__(self, app, parent):
        CtxPlugin.__init__(self, app, parent)
        events.connect(events.DOC_CHANGED, self.update)
        events.connect(events.DOC_MODIFIED, self.update)
        events.connect(events.PAGE_CHANGED, self.update)

    def build(self):
        self.formats = [_('Custom'), ] + PAGE_FORMAT_NAMES
        self.combo = Combolist(self, items=self.formats,
                               onchange=self.combo_changed)
        self.pack(self.combo, padding_all=3)

        self.width_spin = UnitSpin(self.app, self,
                                   onchange=self.width_spin_changed)
        self.pack(self.width_spin)
        self.pack((3, 3))

        self.pack(get_bmp(self, icons.CTX_W_ON_H))

        self.height_spin = UnitSpin(self.app, self,
                                    onchange=self.height_spin_changed)
        self.pack(self.height_spin, padding_all=3)

        self.pack((2, 2))

        self.portrait = ImageToggleButton(self, True, icons.CTX_PAGE_PORTRAIT,
                                          onchange=self.portrait_toggled,
                                          tooltip=ORIENTS_NAMES[0])
        self.pack(self.portrait, padding=2)

        self.landscape = ImageToggleButton(self, False,
                                           icons.CTX_PAGE_LANDSCAPE,
                                           onchange=self.landscape_toggled,
                                           tooltip=ORIENTS_NAMES[1])
        self.pack(self.landscape, padding=2)

        self.width_spin.set_enable(False)
        self.height_spin.set_enable(False)

    def update(self, *args):
        if self.insp.is_doc():
            self.update_flag = True
            page_format = self.app.current_doc.active_page.page_format
            self.format = page_format
            width, height = page_format[1]
            if page_format[0] in PAGE_FORMAT_NAMES:
                self.combo.set_active(self.formats.index(page_format[0]))
                if page_format[2] == PORTRAIT:
                    self.portrait.set_active(True)
                    self.landscape.set_active(False)
                else:
                    self.portrait.set_active(False)
                    self.landscape.set_active(True)
                self.width_spin.set_point_value(width)
                self.height_spin.set_point_value(height)
                self.width_spin.set_enable(False)
                self.height_spin.set_enable(False)
            else:
                self.combo.set_active(self.formats.index(_('Custom')))
                if page_format[2] == PORTRAIT:
                    self.portrait.set_active(True)
                    self.landscape.set_active(False)
                else:
                    self.portrait.set_active(False)
                    self.landscape.set_active(True)
                self.width_spin.set_point_value(width)
                self.height_spin.set_point_value(height)
                self.width_spin.set_enable(True)
                self.height_spin.set_enable(True)
            self.update_flag = False

    def combo_changed(self, *_args):
        if self.update_flag:
            return
        if not self.format[0] == self.formats[self.combo.get_active()]:
            self.update_flag = True
            if self.formats[self.combo.get_active()] in PAGE_FORMAT_NAMES:
                w, h = PAGE_FORMATS[self.formats[self.combo.get_active()]]
                if self.portrait.get_active() and w > h:
                    self.width_spin.set_point_value(w)
                    self.height_spin.set_point_value(h)
                    self.portrait.set_active(False)
                    self.landscape.set_active(True)
                elif self.landscape.get_active() and w > h:
                    self.width_spin.set_point_value(w)
                    self.height_spin.set_point_value(h)
                elif self.portrait.get_active() and w < h:
                    self.width_spin.set_point_value(w)
                    self.height_spin.set_point_value(h)
                else:
                    self.width_spin.set_point_value(h)
                    self.height_spin.set_point_value(w)
            self.update_flag = False
            self.changes()

    def width_spin_changed(self, *_args):
        if self.update_flag:
            return
        if not self.format[1][0] == self.width_spin.get_point_value():
            self.update_flag = True
            w = self.width_spin.get_point_value()
            h = self.height_spin.get_point_value()
            if w > h and self.portrait.get_active():
                self.portrait.set_active(False)
                self.landscape.set_active(True)
            elif w < h and self.landscape.get_active():
                self.portrait.set_active(True)
                self.landscape.set_active(False)
            self.update_flag = False
            self.changes()

    def height_spin_changed(self, *_args):
        if self.update_flag:
            return
        if not self.format[1][1] == self.height_spin.get_point_value():
            self.update_flag = True
            w = self.width_spin.get_point_value()
            h = self.height_spin.get_point_value()
            if w > h and self.portrait.get_active():
                self.portrait.set_active(False)
                self.landscape.set_active(True)
            elif w < h and self.landscape.get_active():
                self.portrait.set_active(True)
                self.landscape.set_active(False)
            self.update_flag = False
            self.changes()

    def portrait_toggled(self, *_args):
        if self.update_flag:
            return
        if self.portrait.get_active():
            self.update_flag = True
            self.landscape.set_active(False)
            h = self.width_spin.get_point_value()
            w = self.height_spin.get_point_value()
            self.width_spin.set_point_value(w)
            self.height_spin.set_point_value(h)
            self.update_flag = False
            self.changes()
        else:
            self.update_flag = True
            self.portrait.set_active(True)
            self.update_flag = False

    def landscape_toggled(self, *_args):
        if self.update_flag:
            return
        if self.landscape.get_active():
            self.update_flag = True
            self.portrait.set_active(False)
            h = self.width_spin.get_point_value()
            w = self.height_spin.get_point_value()
            self.width_spin.set_point_value(w)
            self.height_spin.set_point_value(h)
            self.update_flag = False
            self.changes()
        else:
            self.update_flag = True
            self.landscape.set_active(True)
            self.update_flag = False

    def changes(self):
        doc = self.app.current_doc
        new_format = [self.formats[self.combo.get_active()], ]
        new_format += [(self.width_spin.get_point_value(),
                        self.height_spin.get_point_value())]
        if self.portrait.get_active():
            new_format += [PORTRAIT, ]
        else:
            new_format += [LANDSCAPE, ]
        current_page_format = deepcopy(doc.active_page.page_format)
        doc.api.set_page_format(new_format)

        pdict = PAGE_FORMATS_MORE
        if new_format[0] in pdict and current_page_format[0] in pdids and \
                pdict[current_page_format[0]] != pdict[new_format[0]]:
            units, jump = pdict[new_format[0]]
            doc.api.set_doc_units(units)
            geom = doc.methods.get_grid_values()[:2] + [jump, jump]
            doc.api.set_grid_values(geom)
            config.obj_jump = jump

        doc.canvas.zoom_fit_to_page()


class PageBorderPlugin(CtxPlugin):
    name = 'PageBorderPlugin'
    page_border = None

    def __init__(self, app, parent):
        CtxPlugin.__init__(self, app, parent)

    def build(self):
        btn = ActionButton(self, self.actions[pdids.ID_PAGE_FRAME])
        self.add(btn, 0, LEFT | CENTER, 2)

        # =====
        self.add(VLine(self), 0, ALL | EXPAND, 2)

        self.page_border = UnitSpin(self.app, self, onchange=self.user_changes,
                                    can_be_negative=True)
        self.page_border.set_tooltip(_('Guide frame margin'))
        self.page_border.set_point_value(config.page_border)
        self.add(self.page_border, 0, LEFT | CENTER, 2)

        btn = ActionButton(self, self.actions[pdids.ID_PAGE_GUIDE_FRAME])
        self.add(btn, 0, LEFT | CENTER, 2)

        self.add(VLine(self), 0, ALL | EXPAND, 2)
        # =====

        btn = ActionButton(self, self.actions[pdids.ID_GUIDES_AT_CENTER])
        self.add(btn, 0, LEFT | CENTER, 2)

        btn = ActionButton(self, self.actions[pdids.ID_REMOVE_ALL_GUIDES])
        self.add(btn, 0, LEFT | CENTER, 2)

        btn = ActionToggle(self, self.actions[pdids.ID_LOCK_GUIDES])
        self.add(btn, 0, LEFT | CENTER, 2)

    def user_changes(self, *_args):
        val = self.page_border.get_point_value()
        if not config.page_border == val:
            config.page_border = val
