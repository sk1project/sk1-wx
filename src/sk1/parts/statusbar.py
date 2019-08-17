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
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

import wal
from sk1 import _, config, events
from sk1.pwidgets import SbFillSwatch, SbStrokeSwatch, ActionImageSwitch
from sk1.resources import get_bmp, icons, get_icon
from sk1.resources import pdids, get_tooltip_text
from uc2.uc2const import IMAGE_NAMES, IMAGE_CMYK, IMAGE_RGB
from .menubar import ActionMenuItem

FONTSIZE = [str(config.statusbar_fontsize), ]
LOG = logging.getLogger(__name__)


class AppStatusbar(wal.HPanel):
    mw = None
    mouse_info = None
    page_info = None
    info = None
    panel2 = None
    clr_monitor = None

    def __init__(self, mw):

        if wal.IS_MSW:
            FONTSIZE[0] = 0
        elif not FONTSIZE[0]:
            FONTSIZE[0] = str(wal.get_system_fontsize()[1])

        self.mw = mw
        wal.HPanel.__init__(self, mw)
        self.pack((5, 20))

        self.mouse_info = MouseMonitor(self.mw.app, self)
        self.pack(self.mouse_info, fill=True)
        self.mouse_info.hide()

        self.zoom = ZoomMonitor(self)
        self.pack(self.zoom, fill=True)

        self.snap_monitor = SnapMonitor(self.mw.app, self)
        self.pack(self.snap_monitor, fill=True)

        self.page_info = PageMonitor(self.mw.app, self)
        self.pack(self.page_info, fill=True)
        self.page_info.hide()

        info_panel = wal.HPanel(self)
        info_panel.pack(get_bmp(info_panel, icons.PD_APP_STATUS))
        info_panel.pack((5, 3))
        self.info = wal.Label(info_panel, text='', fontsize=FONTSIZE[0])
        info_panel.pack(self.info)
        self.pack(info_panel, expand=True)

        self.clr_monitor = ColorMonitor(self.mw.app, self)
        self.pack(self.clr_monitor)
        self.clr_monitor.hide()
        events.connect(events.APP_STATUS, self._on_event)

    def _on_event(self, *args):
        self.info.set_text(args[0])
        self.Layout()
        self.show()


class ZoomMonitor(wal.HPanel):
    def __init__(self, parent):
        wal.HPanel.__init__(self, parent)
        icon = get_icon(icons.PD_ZOOM, size=wal.SIZE_16)
        self.pack(wal.Bitmap(self, icon, on_left_click=self.show_menu,
                             on_right_click=self.show_menu))

        self.label = wal.SensitiveLabel(self, '10000%', fontsize=FONTSIZE[0],
                                        on_left_click=self.show_menu,
                                        on_right_click=self.show_menu)
        self.label.set_min_width(65 if wal.IS_MAC else 55)
        self.label.set_tooltip(_('Zoom level'))
        self.pack(self.label, padding=2)

        self.pack(wal.PLine(self.panel), fill=True, padding=3)
        self.zoom_menu = ZoomMenu(parent.mw)

    def update(self, zoom):
        self.label.set_text('%s%%' % int(round(zoom * 100)))

    def show_menu(self, _event):
        self.zoom_menu.rebuild()
        self.popup_menu(self.zoom_menu)


class ZoomMenu(wal.Menu):
    app = None
    mw = None
    items = None
    empty_item = None
    persistent_items = None

    def __init__(self, mw):
        self.app = mw.app
        self.mw = mw
        wal.Menu.__init__(self)
        self.items = []
        self.persistent_items = []

        self.items.append(self.append_separator())
        for pid in [pdids.ID_ZOOM_PAGE, wal.ID_ZOOM_FIT]:
            action = self.app.actions[pid]
            self.append_item(ActionMenuItem(self.mw, self, action))

        self.persistent_items += self.items

    def append_item(self, item):
        self.items.append(item)
        wal.Menu.append_item(self, item)
        if hasattr(item, 'is_separator'):
            item.update()

    def rebuild(self, *_args):
        class ZoomMenuItem(wal.MenuItem):
            app = None
            path = None

            def __init__(self, mw, parent, zoom):
                self.app = mw.app
                self.zoom = zoom
                item_id = wal.new_id()
                txt = '%d%%\tCtrl+F4' % zoom if zoom == 100 else '%d%%' % zoom
                wal.MenuItem.__init__(self, parent, item_id, txt)
                self.bind_to(mw, self.action, item_id)
                if int(round(self.get_zoom())) == self.zoom:
                    self.set_checkable(True)

            def get_zoom(self):
                return self.app.current_doc.canvas.zoom * 100.0

            def update(self):
                if self.is_checkable():
                    self.set_active(True)

            def action(self, _event):
                zoom = float(self.zoom) / self.get_zoom()
                self.app.current_doc.canvas._zoom(zoom)

        for item in self.items:
            self.remove_item(item)
        self.items = []

        entries = [10, 25, 33, 50, 75, 100, 200, 300, 400, 600, 800,
                   1000, 1200, 1600, 2000]
        for entry in entries:
            self.append_item(ZoomMenuItem(self.mw, self, entry))

        for item in self.persistent_items:
            self.append_item(item)


class SnapMonitor(wal.HPanel):
    def __init__(self, app, parent):
        self.app = app
        actions = app.actions
        wal.HPanel.__init__(self, parent)

        action_id = pdids.ID_SNAP_TO_GRID
        tooltip_txt = get_tooltip_text(action_id)
        icons_dict = {
            True: [icons.PD_SNAP_TO_GRID_ON, tooltip_txt],
            False: [icons.PD_SNAP_TO_GRID_OFF, tooltip_txt]}
        sw = ActionImageSwitch(self, actions[action_id], icons_dict)
        self.pack(sw, padding=2)

        action_id = pdids.ID_SNAP_TO_GUIDE
        tooltip_txt = get_tooltip_text(action_id)
        icons_dict = {
            True: [icons.PD_SNAP_TO_GUIDE_ON, tooltip_txt],
            False: [icons.PD_SNAP_TO_GUIDE_OFF, tooltip_txt]}
        sw = ActionImageSwitch(self, actions[action_id], icons_dict)
        self.pack(sw, padding=2)

        action_id = pdids.ID_SNAP_TO_OBJ
        tooltip_txt = get_tooltip_text(action_id)
        icons_dict = {
            True: [icons.PD_SNAP_TO_OBJ_ON, tooltip_txt],
            False: [icons.PD_SNAP_TO_OBJ_OFF, tooltip_txt]}
        sw = ActionImageSwitch(self, actions[action_id], icons_dict)
        self.pack(sw, padding=2)

        action_id = pdids.ID_SNAP_TO_PAGE
        tooltip_txt = get_tooltip_text(action_id)
        icons_dict = {
            True: [icons.PD_SNAP_TO_PAGE_ON, tooltip_txt],
            False: [icons.PD_SNAP_TO_PAGE_OFF, tooltip_txt]}
        sw = ActionImageSwitch(self, actions[action_id], icons_dict)
        self.pack(sw, padding=2)

        self.pack(wal.PLine(self.panel), fill=True, padding=5)


class ColorMonitor(wal.HPanel):
    image_txt = None
    fill_txt = None
    fill_swatch = None
    stroke_txt = None
    stroke_swatch = None

    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        wal.HPanel.__init__(self, parent)

        self.image_txt = wal.Label(
            self, text=_('Image type: '), fontsize=FONTSIZE[0])
        self.pack(self.image_txt, padding=4)
        self.fill_txt = wal.Label(self, text=_('Fill:'), fontsize=FONTSIZE[0])
        self.pack(self.fill_txt)
        self.fill_swatch = SbFillSwatch(
            self, self.app, self.fill_txt, onclick=self.app.proxy.fill_dialog)
        self.pack(self.fill_swatch, padding=2)
        self.pack((5, 5))
        self.stroke_txt = wal.Label(
            self, text=_('Stroke:'), fontsize=FONTSIZE[0])
        self.pack(self.stroke_txt)
        self.stroke_swatch = SbStrokeSwatch(
            self, self.app, self.stroke_txt,
            onclick=self.app.proxy.stroke_dialog)
        self.pack(self.stroke_swatch, padding=2)
        self.pack((5, 5))
        self.Layout()
        events.connect(events.SELECTION_CHANGED, self.update)
        events.connect(events.DOC_CHANGED, self.update)
        events.connect(events.NO_DOCS, self.update)

    def update(self, *_args):
        if not self.app.current_doc:
            return
        sel = self.app.current_doc.get_selected_objs()
        if sel:
            if len(sel) == 1 and self.app.insp.is_obj_primitive(sel[0]):
                self.fill_swatch.update_from_obj(sel[0])
                self.stroke_swatch.update_from_obj(sel[0])
                if self.app.insp.is_obj_pixmap(sel[0]):
                    txt = _('Image type: ') + IMAGE_NAMES[sel[0].colorspace]
                    if sel[0].has_alpha():
                        if sel[0].colorspace in [IMAGE_CMYK, IMAGE_RGB]:
                            txt += 'A'
                        else:
                            txt += '+A'
                    self.image_txt.set_text(txt)
                    self.image_txt.show()
                else:
                    self.image_txt.hide()
                if not self.is_shown():
                    self.show()
                self.parent.layout()
                return
        self.hide()


class MouseMonitor(wal.HPanel):
    def __init__(self, app, parent):
        self.app = app
        wal.HPanel.__init__(self, parent)
        self.pack(get_bmp(self.panel, icons.PD_MOUSE_MONITOR), padding_all=3)
        self.pointer_txt = wal.Label(self.panel, text=' ', fontsize=FONTSIZE[0])
        self.pointer_txt.set_min_width(130 if wal.IS_MAC else 100)
        self.pack(self.pointer_txt)
        self.pack(wal.PLine(self.panel), fill=True, padding=3)
        events.connect(events.MOUSE_STATUS, self.set_value)
        events.connect(events.NO_DOCS, self.hide_monitor)
        events.connect(events.DOC_CHANGED, self.doc_changed)

    def clear(self):
        self.pointer_txt.set_text(' ' + _('No coords'))

    def hide_monitor(self, *_args):
        self.hide()
        self.clear()

    def set_value(self, *args):
        self.pointer_txt.set_text(args[0])

    def doc_changed(self, *_args):
        self.clear()
        if not self.is_shown():
            self.show()


class PageMonitor(wal.HPanel):
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        wal.HPanel.__init__(self, parent)

        native = False
        if wal.IS_GTK:
            native = True

        callback = self.app.proxy.goto_start
        self.start_but = wal.ImageButton(
            self.panel, icons.PD_PM_ARROW_START,
            tooltip=_('Go to fist page'),
            decoration_padding=4,
            native=native,
            onclick=callback)
        self.pack(self.start_but)

        callback = self.app.proxy.previous_page
        self.prev_but = wal.ImageButton(
            self.panel,
            icons.PD_PM_ARROW_LEFT,
            tooltip=_('Go to previous page'),
            decoration_padding=4,
            native=native,
            onclick=callback)
        self.pack(self.prev_but)

        self.page_txt = wal.Label(self.panel, text=' ', fontsize=FONTSIZE[0])
        self.pack(self.page_txt)

        callback = self.app.proxy.next_page
        self.next_but = wal.ImageButton(
            self.panel,
            icons.PD_PM_ARROW_RIGHT,
            tooltip=_('Go to next page'),
            decoration_padding=4,
            native=native,
            onclick=callback)
        self.pack(self.next_but)

        callback = self.app.proxy.goto_end
        self.end_but = wal.ImageButton(
            self.panel,
            icons.PD_PM_ARROW_END,
            tooltip=_('Go to last page'),
            decoration_padding=4,
            native=native,
            onclick=callback)
        self.pack(self.end_but)

        self.pack(wal.VLine(self.panel), fill=True, padding=4)
        events.connect(events.NO_DOCS, self.hide_monitor)
        events.connect(events.DOC_CHANGED, self.update)
        events.connect(events.DOC_MODIFIED, self.update)
        events.connect(events.PAGE_CHANGED, self.update)

    def update(self, *_args):
        if self.app.current_doc:
            presenter = self.app.current_doc
            pages = presenter.get_pages()
            if len(pages) == 1:
                self.hide()
                return
            current_index = pages.index(presenter.active_page)

            if current_index:
                self.start_but.set_enable(True)
                self.prev_but.set_enable(True)
            else:
                self.start_but.set_enable(False)
                self.prev_but.set_enable(False)

            if current_index == len(pages) - 1:
                self.end_but.set_enable(False)
            else:
                self.end_but.set_enable(True)

            text = _("Page %i of %i") % (current_index + 1, len(pages))
            self.page_txt.set_text(' %s ' % text)
            self.show()

    def hide_monitor(self, *_args):
        self.hide()
