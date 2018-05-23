# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015-2016 by Igor E. Novikov
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

from copy import deepcopy

import wal
from dashedit_dlg import dash_editor_dlg
from sk1 import _, config
from sk1.pwidgets import SolidFill, StaticUnitLabel, UnitSpin, DashChoice, \
    CapChoice, JoinChoice, ArrowChoice
from sk1.resources import icons
from uc2 import uc2const

FALLBACK_STROKE = [0, 0.28346456692913385,
                   [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 1.0], 1.0, ''],
                   [], 1, 0, -2.0526525391269526, 0, 0, []]


class StrokeDialog(wal.OkCancelDialog):
    color_tab = None
    stroke_tab = None
    presenter = None
    orig_stroke = None
    new_stroke = None
    orig_color = None
    new_color = None
    nb = None

    def __init__(self, parent, title, presenter, stroke_style=None):
        stroke_style = stroke_style or None
        self.presenter = presenter
        self.app = presenter.app
        self.orig_stroke = stroke_style
        if self.orig_stroke:
            self.new_stroke = deepcopy(stroke_style)
            self.orig_color = stroke_style[2]
            self.new_color = deepcopy(stroke_style[2])
        else:
            self.new_stroke = deepcopy(FALLBACK_STROKE)
            self.orig_color = []
            self.new_color = []
        size = config.stroke_dlg_size
        wal.OkCancelDialog.__init__(self, parent, title, style=wal.VERTICAL,
                                    resizable=True, size=size, add_line=False,
                                    action_button=wal.BUTTON_APPLY)
        self.set_minsize(config.stroke_dlg_minsize)

    def build(self):
        self.nb = wal.Notebook(self)
        self.color_tab = StrokeColor(self.nb, self, self.orig_color)
        self.stroke_tab = StrokeStyle(self.nb, self, self.new_stroke)
        self.nb.add_page(self.color_tab, _('Stroke Color'))
        self.nb.add_page(self.stroke_tab, _('Stroke Style'))
        if self.new_color:
            self.nb.set_active_index(1)
        else:
            self.nb.remove_page_by_index(1)
        self.pack(self.nb, fill=True, expand=True)

    def set_color(self, color):
        if not self.new_color and color:
            self.nb.add_page(self.stroke_tab, _('Stroke Style'))
        self.new_color = color
        if not self.new_color and self.stroke_tab:
            self.nb.remove_page(self.stroke_tab)

    def get_result(self):
        if self.new_color:
            self.new_stroke = self.stroke_tab.get_stroke()
            self.new_stroke[2] = self.color_tab.get_color()
            return self.new_stroke
        return []

    def show(self):
        ret = None
        if self.show_modal() == wal.BUTTON_OK:
            ret = self.get_result()
        w, h = self.get_size()
        if wal.is_unity_16_04():
            h = max(h - 28, config.stroke_dlg_minsize[1])
        config.stroke_dlg_size = (w, h)
        self.destroy()
        return ret


def stroke_dlg(parent, presenter, stroke_style, title=_('Stroke')):
    return StrokeDialog(parent, title, presenter, stroke_style).show()


class StrokeStyle(wal.VPanel):
    def __init__(self, parent, dlg, new_stroke):
        self.dlg = dlg
        self.app = dlg.app
        self.stroke = new_stroke
        wal.VPanel.__init__(self, parent)

        hp = wal.HPanel(self)

        width_p = wal.LabeledPanel(hp, _('Width:'))
        p = wal.HPanel(width_p)
        self.width_spin = UnitSpin(self.app, p, self.stroke[1], step=0.1)
        p.pack(self.width_spin)
        p.pack((5, 5))
        p.pack(StaticUnitLabel(self.app, p))
        width_p.pack(p, padding_all=5)
        hp.pack(width_p, fill=True)

        hp.pack((5, 5))
        arrow_p = wal.LabeledPanel(hp, _('Arrows:'))

        p = wal.HPanel(arrow_p)

        self.end_arrow = ArrowChoice(p, end=True)
        p.pack(self.end_arrow)
        p.pack((5, 5))
        self.start_arrow = ArrowChoice(p)
        p.pack(self.start_arrow)

        arrow_p.pack(p)

        hp.pack(arrow_p, expand=True, fill=True)
        self.pack(hp, fill=True, padding_all=10)

        p = wal.HPanel(self)
        p.pack(wal.Label(p, _('Dashes:')), padding=5)
        self.dashes = DashChoice(p, self.stroke[3])
        p.pack(self.dashes)
        txt = _('Edit dash pattern')
        p.pack(wal.ImageButton(p, icons.PD_EDIT, art_size=wal.SIZE_16,
                               tooltip=txt, flat=False,
                               onclick=self.edit_dash), padding=5)
        self.pack(p)

        grid = wal.GridPanel(self, rows=1, cols=3, vgap=15, hgap=15)
        grid.add_growable_col(2)

        caps_p = wal.LabeledPanel(grid, _('Caps:'))
        self.caps = CapChoice(caps_p, self.stroke[4])
        caps_p.pack(self.caps, align_center=False, padding_all=10)
        grid.pack(caps_p)

        join_p = wal.LabeledPanel(grid, _('Join:'))
        self.join = JoinChoice(join_p, self.stroke[5])
        join_p.pack(self.join, align_center=False, padding_all=10)
        grid.pack(join_p)

        opt_p = wal.LabeledPanel(grid, _('Options:'))

        p = wal.HPanel(opt_p)
        p.pack(wal.Label(p, _('Miter limit:')), padding=5)
        self.miter_limit = wal.FloatSpin(p, self.stroke[6],
                                         range_val=(0.0, 1000.0), digits=5)
        p.pack(self.miter_limit)
        opt_p.pack(p, align_center=False, padding_all=10)

        p = wal.VPanel(opt_p)
        self.behind = wal.NumCheckbox(p, _('Behind fill'), self.stroke[7])
        p.pack(self.behind, align_center=False)

        self.scalable = wal.NumCheckbox(p, _('Scalable stroke'), self.stroke[8])
        p.pack(self.scalable, align_center=False, padding=10)
        opt_p.pack(p, align_center=False, padding_all=10)

        grid.pack(opt_p, fill=True)

        self.pack(grid, padding_all=10, fill=True)
        self.layout()

    def edit_dash(self):
        ret = dash_editor_dlg(self.dlg, self.dashes.get_dash())
        if ret is not None:
            self.dashes.set_dash(ret)

    def get_stroke(self):
        self.stroke[1] = self.width_spin.get_point_value()
        self.stroke[3] = self.dashes.get_dash()
        self.stroke[4] = self.caps.get_cap()
        self.stroke[5] = self.join.get_join()
        self.stroke[6] = self.miter_limit.get_value()
        self.stroke[7] = self.behind.get_value()
        self.stroke[8] = self.scalable.get_value()
        return self.stroke


class StrokeColor(wal.VPanel):
    def __init__(self, parent, dlg, orig_color):
        self.dlg = dlg
        wal.VPanel.__init__(self, parent)
        cms = dlg.presenter.cms
        self.color_panel = SolidFill(self, dlg, cms)
        self.pack(self.color_panel, fill=True, expand=True)
        fill = []
        if orig_color:
            fill = [0, 0, orig_color]
        self.color_panel.activate(fill, use_rule=False,
                                  onmodechange=self.on_mode_change)

    def on_mode_change(self):
        self.dlg.set_color(self.get_color())

    def get_color(self):
        fill = self.color_panel.get_result()
        if fill:
            return fill[2]
        return []
