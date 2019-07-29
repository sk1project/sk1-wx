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

from base64 import b64decode, b64encode
from copy import deepcopy

import wal
from sk1 import _, config
from sk1.pwidgets import StaticUnitLabel, UnitSpin, CBMiniPalette
from sk1.resources import icons, get_bmp, pdids
from uc2 import cms, uc2const
from uc2.sk2const import ORIGINS, FILL_SOLID, FILL_PATTERN
from uc2.uc2const import unit_names, unit_full_names, ORIENTS_NAMES
from . import docinfodlg


class DocPropsPanel(wal.VPanel):
    name = 'Panel'

    def __init__(self, parent, app, dlg):
        self.app = app
        self.dlg = dlg
        self.doc = app.current_doc
        self.api = self.doc.api
        wal.VPanel.__init__(self, parent)
        self.build()

    def build(self): pass

    def save(self): pass


class GeneralProps(DocPropsPanel):
    name = _('Description')
    metainfo = None
    author_field = None
    license_field = None
    keys_field = None
    notes_field = None

    def build(self):
        self.metainfo = deepcopy(self.doc.model.metainfo)
        if self.metainfo[3]:
            self.metainfo[3] = b64decode(self.metainfo[3])

        grid = wal.GridPanel(self, 4, 2, 5, 5)
        grid.add_growable_col(1)
        grid.add_growable_row(3)

        grid.pack(wal.Label(grid, _('Author:')))
        self.author_field = wal.Entry(grid, self.metainfo[0])
        grid.pack(self.author_field, fill=True)

        grid.pack(wal.Label(grid, _('License:')))
        self.license_field = wal.Entry(grid, self.metainfo[1])
        grid.pack(self.license_field, fill=True)

        grid.pack(wal.Label(grid, _('Keywords:')))
        self.keys_field = wal.Entry(grid, self.metainfo[2])
        grid.pack(self.keys_field, fill=True)

        grid.pack(wal.Label(grid, _('Notes:')))
        self.notes_field = wal.Entry(grid, self.metainfo[3], multiline=True)
        grid.pack(self.notes_field, fill=True)

        self.pack(grid, fill=True, expand=True, padding_all=5)

    def save(self):
        metainfo = [self.author_field.get_value(),
                    self.license_field.get_value(),
                    self.keys_field.get_value(),
                    self.notes_field.get_value()]
        if not self.metainfo == metainfo:
            if metainfo[3]:
                metainfo[3] = b64encode(metainfo[3])
            self.api.set_doc_metainfo(metainfo)


ORIENTS = [uc2const.PORTRAIT, uc2const.LANDSCAPE]
ORIENTS_ICONS = [icons.CTX_PAGE_PORTRAIT, icons.CTX_PAGE_LANDSCAPE]


class PageProps(DocPropsPanel):
    name = _('Page')
    page_format = None
    desktop_bg = None
    page_fill = None
    border_flag = False
    formats = None
    as_current = None

    page_combo = None
    orient_keeper = None
    page_width = None
    page_height = None
    desktop_color_btn = None
    page_color1_btn = None
    page_color2_btn = None
    colors2 = None
    pattern_check = None
    border_check = None

    def build(self):
        self.page_format = self.doc.methods.get_default_page_format()

        self.formats = [_('Custom'), ] + uc2const.PAGE_FORMAT_NAMES
        self.pack((5, 10))

        # ---
        hpanel = wal.HPanel(self)
        hpanel.pack((5, 5))
        label = wal.Label(hpanel, _('Default page:'))
        hpanel.pack(label)
        hpanel.pack((5, 5))
        self.page_combo = wal.Combolist(self, items=self.formats,
                                        onchange=self.page_combo_changed)

        hpanel.pack(self.page_combo)

        hpanel.pack((15, 5))

        self.orient_keeper = wal.HToggleKeeper(self, ORIENTS, ORIENTS_ICONS,
                                               ORIENTS_NAMES,
                                               on_change=self.orient_changed)
        hpanel.pack(self.orient_keeper)

        hpanel.pack((5, 5))

        self.as_current = wal.Button(hpanel, ' %s ' % _('As current page'),
                               onclick=self.set_as_current)
        hpanel.pack(self.as_current)

        self.pack(hpanel, fill=True)

        self.pack((5, 5))

        # ---
        hpanel = wal.HPanel(self)
        dx = label.get_size()[0] + 10
        hpanel.pack((dx, 5))

        self.page_width = UnitSpin(self.app, hpanel, 0,
                                   onchange=self.page_spin_changed)
        hpanel.pack(self.page_width)
        hpanel.pack(get_bmp(self, icons.CTX_W_ON_H), padding=5)
        self.page_height = UnitSpin(self.app, hpanel, 0,
                                    onchange=self.page_spin_changed)
        hpanel.pack(self.page_height)
        hpanel.pack(StaticUnitLabel(self.app, hpanel), padding=5)

        self.pack(hpanel, fill=True)
        self.pack(wal.HLine(self), padding_all=5, fill=True)

        self.set_page_format(self.page_format)

        # --- COLORS
        hpanel = wal.HPanel(self)
        hpanel.pack((5, 5))
        self.desktop_bg = self.doc.methods.get_desktop_bg()

        grid = wal.GridPanel(hpanel, 3, 3, 5, 5)
        grid.add_growable_col(2)

        grid.pack(wal.Label(hpanel, _('Desktop:')))
        self.desktop_color_btn = wal.ColorButton(hpanel, self.desktop_bg)
        grid.pack(self.desktop_color_btn)
        grid.pack(CBMiniPalette(grid, onclick=self.desktop_color_btn.set_value))

        self.page_fill = self.doc.methods.get_page_fill()
        if self.page_fill[0] == FILL_SOLID:
            color1 = self.page_fill[1]
            color2 = [1.0, 1.0, 1.0]
        else:
            color1 = self.page_fill[1][0]
            color2 = self.page_fill[1][1]

        grid.pack(wal.Label(hpanel, _('Page:')))
        self.page_color1_btn = wal.ColorButton(hpanel, color1)
        grid.pack(self.page_color1_btn)
        grid.pack(CBMiniPalette(grid, onclick=self.page_color1_btn.set_value))

        grid.pack((5, 5))
        self.page_color2_btn = wal.ColorButton(hpanel, color2)
        grid.pack(self.page_color2_btn)
        self.colors2 = CBMiniPalette(grid,
                                     onclick=self.page_color2_btn.set_value)
        grid.pack(self.colors2)
        if not self.page_fill[0] == FILL_PATTERN:
            self.page_color2_btn.set_enable(False)
            self.colors2.set_enable(False)

        hpanel.pack(grid, fill=True)
        hpanel.pack((5, 5))
        self.pack(hpanel, fill=True)


        # ---
        vpanel = wal.VPanel(self)
        if wal.IS_MSW:
            vpanel.pack((5, 5))

        self.pattern_check = wal.Checkbox(vpanel,
                                          _('Use pattern for page fill'),
                                          self.page_fill[0] == FILL_PATTERN,
                                          onclick=self.pattern_check_changed)
        vpanel.pack(self.pattern_check, align_center=False)

        if wal.IS_MSW:
            vpanel.pack((5, 5))

        self.border_flag = self.doc.methods.get_page_border()
        self.border_check = wal.Checkbox(vpanel,
                                         _('Show page border'),
                                         self.border_flag)
        vpanel.pack(self.border_check, align_center=False)
        self.pack(vpanel, fill=True, padding_all=5)

    def set_page_format(self, page_format):
        index = 0
        state = True
        if page_format[0] in uc2const.PAGE_FORMAT_NAMES:
            index = self.formats.index(page_format[0])
            state = False
        self.page_combo.set_active(index)
        self.orient_keeper.set_mode(page_format[2])

        w, h = page_format[1]
        self.page_width.set_point_value(w)
        self.page_height.set_point_value(h)

        self.page_width.set_enable(state)
        self.page_height.set_enable(state)

        current_page_format = self.app.current_doc.active_page.page_format
        self.as_current.set_enable(current_page_format != page_format)

    def set_as_current(self):
        page_format = deepcopy(self.app.current_doc.active_page.page_format)
        self.set_page_format(page_format)

    def page_combo_changed(self):
        state = False
        if not self.page_combo.get_active():
            state = True
        else:
            w, h = uc2const.PAGE_FORMATS[self.page_combo.get_active_value()]
            self.page_width.set_point_value(w)
            self.page_height.set_point_value(h)
            self.orient_keeper.set_mode(uc2const.PORTRAIT)
        self.page_width.set_enable(state)
        self.page_height.set_enable(state)

    def page_spin_changed(self):
        w = self.page_width.get_point_value()
        h = self.page_height.get_point_value()
        if w < h:
            mode = uc2const.PORTRAIT
        else:
            mode = uc2const.LANDSCAPE
        self.orient_keeper.set_mode(mode)

    def orient_changed(self, mode):
        w = self.page_width.get_point_value()
        h = self.page_height.get_point_value()
        w, h = h, w
        self.page_width.set_point_value(w)
        self.page_height.set_point_value(h)

    def pattern_check_changed(self):
        state = self.pattern_check.get_value()
        self.page_color2_btn.set_enable(state)
        self.colors2.set_enable(state)

    def save(self):
        page_format = [self.page_combo.get_active_value(),
                       (self.page_width.get_point_value(),
                        self.page_height.get_point_value(), ),
                       self.orient_keeper.get_mode()]
        if self.page_format != page_format:
            self.api.set_default_page_format(page_format)
        desktop_bg = self.desktop_color_btn.get_value()
        if self.desktop_bg != desktop_bg:
            self.api.set_desktop_bg(desktop_bg)

        color1 = self.page_color1_btn.get_value()
        if self.pattern_check.get_value():
            color2 = self.page_color2_btn.get_value()
            page_fill = [FILL_PATTERN, [color1, color2]]
        else:
            page_fill = [FILL_SOLID, color1]
        if not self.page_fill == page_fill:
            self.api.set_page_fill(page_fill)

        visibility = self.app.insp.is_draw_page_border()
        if not visibility == self.border_check.get_value():
            self.app.actions[pdids.ID_SHOW_PAGE_BORDER]()


ORIGIN_ICONS = [icons.L_ORIGIN_CENTER, icons.L_ORIGIN_LL, icons.L_ORIGIN_LU]
ORIGIN_NAMES = [_('Page center'),
                _('Left lower page corner'), _('Left upper page corner')]


class UnitsProps(DocPropsPanel):
    name = _('Units')
    units = 'mm'
    origin = 0

    units_combo = None
    origin_keeper = None

    def build(self):

        self.pack((5, 5))

        hpanel = wal.HPanel(self)

        vp = wal.LabeledPanel(hpanel, text=_('Document units'))
        names = []
        for item in unit_names:
            names.append(unit_full_names[item])
        self.units_combo = wal.Combolist(vp, items=names)
        self.units = self.doc.methods.get_doc_units()
        self.units_combo.set_active(unit_names.index(self.units))
        vp.pack(self.units_combo, padding_all=15, fill=True)
        hpanel.pack(vp, expand=True, fill=True)

        hpanel.pack((10, 10))

        vp = wal.LabeledPanel(hpanel, text=_('Document origin'))
        self.origin = self.doc.methods.get_doc_origin()
        self.origin_keeper = wal.HToggleKeeper(vp, ORIGINS, ORIGIN_ICONS,
                                               ORIGIN_NAMES)
        self.origin_keeper.set_mode(self.origin)
        vp.pack(self.origin_keeper, padding_all=5)
        hpanel.pack(vp, fill=True)

        self.pack(hpanel, fill=True, padding_all=5)

        data = [[_('Unit'), _('Value in points')]]
        for item in uc2const.unit_names:
            name = uc2const.unit_full_names[item]
            value = _('%s points') % str(uc2const.unit_dict[item])
            data.append([name, value])
        slist = wal.ReportList(self, data)
        self.pack(slist, expand=True, fill=True, padding_all=5)
        self.pack((5, 5))

    def save(self):
        units = unit_names[self.units_combo.get_active()]
        if not self.units == units:
            self.api.set_doc_units(units)
        if not self.origin == self.origin_keeper.get_mode():
            self.api.set_doc_origin(self.origin_keeper.get_mode())


WIDTH = 300


class GridPreview(wal.VPanel, wal.Canvas):
    color = []
    vgrid = range(0, WIDTH, 20)
    hgrid = range(0, WIDTH, 20)

    def __init__(self, parent, color):
        self.color = color
        wal.VPanel.__init__(self, parent, True)
        wal.Canvas.__init__(self)
        self.set_bg(wal.WHITE)

    def set_color(self, color):
        self.color = color
        self.refresh()

    def _composite_color(self, color1, color2=None):
        color2 = color2 or [1.0, 1.0, 1.0]
        r0, g0, b0, a0 = color1
        r1, g1, b1 = color2
        a1 = 1.0 - a0
        r = r0 * a0 + r1 * a1
        g = g0 * a0 + g1 * a1
        b = b0 * a0 + b1 * a1
        return [r, g, b]

    def paint(self):
        color1 = self._composite_color(self.color)
        color2 = self._composite_color(self.color, color1)

        self.set_stroke(cms.val_255(color1), 1.0)
        for item in self.vgrid:
            self.draw_line(item, 0, item, WIDTH)
        for item in self.hgrid:
            self.draw_line(0, item, WIDTH, item)
        self.draw_line(0, self.get_size()[1] - 1, 200, self.get_size()[1] - 1)

        self.set_stroke(cms.val_255(color2), 1.0)
        self.draw_line(self.vgrid[2], 0, self.vgrid[2], WIDTH)
        self.draw_line(0, self.hgrid[3], WIDTH, self.hgrid[3])

        self.set_stroke(cms.val_255(color2), 1.0)
        self.set_fill(None)
        w, h = self.get_size()
        self.draw_rect(0, 0, w, h)


class GridProps(DocPropsPanel):
    name = _('Grid')
    geom = []
    color = []

    x_val = None
    y_val = None
    dx_val = None
    dy_val = None
    grid_color_btn = None
    alpha_spin = None
    alpha_slider = None
    show_grid_check = None
    grid_preview = None

    def build(self):
        self.pack((5, 5))

        self.geom = self.doc.methods.get_grid_values()
        hpanel = wal.HPanel(self)

        txt = _('Grid origin')
        origin_panel = wal.LabeledPanel(hpanel, text=txt)
        grid = wal.GridPanel(origin_panel, 2, 3, 5, 5)

        grid.pack(wal.Label(grid, 'X:'))
        self.x_val = UnitSpin(self.app, grid, self.geom[0])
        grid.pack(self.x_val)
        grid.pack(StaticUnitLabel(self.app, grid))

        grid.pack(wal.Label(grid, 'Y:'))
        self.y_val = UnitSpin(self.app, grid, self.geom[1])
        grid.pack(self.y_val)
        grid.pack(StaticUnitLabel(self.app, grid))

        origin_panel.pack(grid, padding_all=5)
        hpanel.pack(origin_panel, padding_all=5, fill=True, expand=True)

        txt = _('Grid frequency')
        freq_panel = wal.LabeledPanel(hpanel, text=txt)
        grid = wal.GridPanel(origin_panel, 2, 3, 5, 5)

        grid.pack(wal.Label(grid, 'dX:'))
        self.dx_val = UnitSpin(self.app, grid, self.geom[2])
        grid.pack(self.dx_val)
        grid.pack(StaticUnitLabel(self.app, grid))

        grid.pack(wal.Label(grid, 'dY:'))
        self.dy_val = UnitSpin(self.app, grid, self.geom[3])
        grid.pack(self.dy_val)
        grid.pack(StaticUnitLabel(self.app, grid))

        freq_panel.pack(grid, padding_all=5)
        hpanel.pack(freq_panel, padding_all=5, fill=True, expand=True)

        self.pack(hpanel, fill=True)

        self.pack((5, 5))

        color_panel = wal.HPanel(self)

        color_panel.pack((10, 10))

        vpanel = wal.VPanel(color_panel)

        hpanel = wal.HPanel(vpanel)
        hpanel.pack(wal.Label(hpanel, _('Grid color:')))
        hpanel.pack((10, 5))
        self.color = self.doc.methods.get_grid_rgba_color()
        self.grid_color_btn = wal.ColorButton(hpanel, self.color[:3],
                                              onchange=self.on_change)
        hpanel.pack(self.grid_color_btn)
        vpanel.pack(hpanel, fill=True)

        hpanel = wal.HPanel(vpanel)
        hpanel.pack(wal.Label(hpanel, _('Grid opacity:')))
        hpanel.pack((10, 5))
        self.alpha_spin = wal.FloatSpin(hpanel, self.color[3] * 100.0,
                                        range_val=(0.0, 100.0),
                                        onchange=self.on_spin_change,
                                        onenter=self.on_spin_change)
        hpanel.pack(self.alpha_spin)
        hpanel.pack(wal.Label(hpanel, '%'), padding=3)

        vpanel.pack(hpanel, fill=True, padding=5)

        self.alpha_slider = wal.Slider(vpanel, int(self.color[3] * 100.0),
                                       range_val=(0, 100),
                                       onchange=self.on_slider_change)
        vpanel.pack(self.alpha_slider, fill=True, padding=5)

        val = self.doc.methods.is_grid_visible()
        self.show_grid_check = wal.Checkbox(vpanel,
                                            _('Show grid on canvas'), val)
        vpanel.pack(self.show_grid_check, fill=True, padding=5)

        color_panel.pack(vpanel)

        color_panel.pack((10, 10))

        preview_panel = wal.VPanel(color_panel)
        preview_panel.pack(wal.Label(hpanel, _('Grid preview:')))
        preview_panel.pack((5, 5))
        self.grid_preview = GridPreview(preview_panel, self.color)
        preview_panel.pack(self.grid_preview, fill=True, expand=True)
        preview_panel.pack((5, 5))
        color_panel.pack(preview_panel, fill=True, expand=True)

        color_panel.pack((10, 10))

        self.pack(color_panel, fill=True, expand=True)

    def on_slider_change(self):
        self.alpha_spin.set_value(float(self.alpha_slider.get_value()))
        self.on_change()

    def on_spin_change(self):
        self.alpha_slider.set_value(int(self.alpha_spin.get_value()))
        self.on_change()

    def on_change(self):
        color = list(self.grid_color_btn.get_value())
        color.append(self.alpha_spin.get_value() / 100.0)
        self.grid_preview.set_color(color)

    def save(self):
        geom = [self.x_val.get_point_value(), self.y_val.get_point_value(),
                self.dx_val.get_point_value(), self.dy_val.get_point_value()]
        if not self.geom == geom:
            self.api.set_grid_values(geom)
        color = list(self.grid_color_btn.get_value())
        color.append(self.alpha_spin.get_value() / 100.0)
        if not self.color == color:
            self.api.set_grid_color(color)
        visibility = self.app.insp.is_grid_visible()
        if not visibility == self.show_grid_check.get_value():
            self.app.actions[pdids.ID_SHOW_GRID]()


class GuidePreview(wal.VPanel, wal.Canvas):
    color = []

    def __init__(self, parent, color):
        self.color = color
        wal.VPanel.__init__(self, parent, True)
        wal.Canvas.__init__(self)
        self.set_bg(wal.WHITE)

    def set_color(self, color):
        self.color = color
        self.refresh()

    def paint(self):
        self.set_stroke(cms.val_255(self.color), 1.0, config.guide_line_dash)
        w, h = self.get_size()

        for item in (0.4, 0.5, 0.8):
            self.draw_line(int(item * w), 0, int(item * w), h)
        for item in (0.3, 0.7):
            self.draw_line(0, int(item * h), w, int(item * h))

        self.set_stroke(wal.UI_COLORS['hover_solid_border'])
        self.set_fill(None)
        self.draw_rect(0, 0, w, h)


GUIDE_COLORS = ['#0051FF', '#7DF7F6', '#503E8C', '#FF3C0B', '#8282FF',
                '#BEBEBE']


class GuidesProps(DocPropsPanel):
    name = _('Guides')
    color = []

    guide_color_btn = None
    show_guide_check = None
    edit_guide_check = None
    preview = None

    def build(self):

        self.pack((5, 5))

        vpanel = wal.VPanel(self)

        hpanel = wal.HPanel(vpanel)
        hpanel.pack(wal.Label(hpanel, _('Guide color:')))
        hpanel.pack((10, 5))
        self.color = self.doc.methods.get_guide_rgb_color()
        self.guide_color_btn = wal.ColorButton(hpanel, self.color[:3],
                                               onchange=self.on_change)
        hpanel.pack(self.guide_color_btn)
        hpanel.pack((10, 5))
        hpanel.pack(CBMiniPalette(hpanel, colors=GUIDE_COLORS,
                                  onclick=self.change_color))
        vpanel.pack(hpanel, fill=True, align_center=False)

        hpanel = wal.HPanel(vpanel)

        val = self.doc.methods.is_guide_visible()
        self.show_guide_check = wal.Checkbox(hpanel, _('Show guides on canvas'),
                                             val)
        hpanel.pack(self.show_guide_check)

        val = self.doc.methods.is_guide_editable()
        self.edit_guide_check = wal.Checkbox(hpanel, _('Edit guides'), val)
        hpanel.pack(self.edit_guide_check, padding=10)

        vpanel.pack(hpanel, fill=True, padding=5)

        self.pack((10, 10))

        self.preview = GuidePreview(vpanel, deepcopy(self.color))
        vpanel.pack(self.preview, fill=True, expand=True)

        self.pack(vpanel, fill=True, expand=True, padding_all=5)

    def on_change(self):
        self.preview.set_color(self.guide_color_btn.get_value())

    def change_color(self, color):
        self.guide_color_btn.set_value(color)
        self.on_change()

    def save(self):
        color = list(self.guide_color_btn.get_value())
        if not self.color == color:
            self.api.set_guide_color(color)
        visibility = self.app.insp.is_guides_visible()
        if not visibility == self.show_guide_check.get_value():
            self.app.actions[pdids.ID_SHOW_GUIDES]()
        editable = self.app.insp.is_guides_editable()
        if not editable == self.edit_guide_check.get_value():
            self.api.set_guide_editable(not editable)


PANELS = [GeneralProps, PageProps, UnitsProps, GridProps, GuidesProps]


class DocPropertiesDialog(wal.OkCancelDialog):
    sizer = None
    app = None
    panels = []

    def __init__(self, app, parent, title):
        self.app = app
        size = config.docprops_dlg_size
        wal.OkCancelDialog.__init__(self, parent, title, size,
                                    resizable=True, add_line=False)
        self.info_btn = wal.Button(self.button_box, _('Statistics...'),
                                   tooltip=_("Document info"),
                                   onclick=self.on_info, default=True)
        self.left_button_box.pack(self.info_btn, padding=2)
        self.set_minsize(config.docprops_dlg_minsize)

    def on_info(self):
        docinfodlg.docinfo_dlg(self.app, self)

    def build(self):
        self.panels = []
        nb = wal.Notebook(self)
        for item in PANELS:
            item_panel = item(nb, self.app, self)
            self.panels.append(item_panel)
            nb.add_page(item_panel, item_panel.name)
        self.pack(nb, expand=True, fill=True, padding=5)

    def get_result(self):
        for item in self.panels:
            item.save()

    def show(self):
        if self.show_modal() == wal.BUTTON_OK:
            self.get_result()
        w, h = self.get_size()
        if wal.is_unity_16_04():
            h = max(h - 28, config.docprops_dlg_minsize[1])
        config.docprops_dlg_size = (w, h)
        self.destroy()


def docprops_dlg(app, parent):
    title = _('Document properties')
    DocPropertiesDialog(app, parent, title).show()
