# -*- coding: utf-8 -*-
#
#  Copyright (C) 2019 Maxim. S. Barabash
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

from sk1 import _, config
from sk1.resources import icons

from generic import PrefPanel


NODE_SIZE_SCHEME = [_('Small'), _('Medium'), _('Large')]
NODE_SIZE = [5, 7, 9]


class EditPrefs(PrefPanel):
    pid = 'Edit'
    name = _('Edit')
    title = _('Edit preferences')
    icon_id = icons.PD_PREFS_EDIT

    def __init__(self, app, dlg, *args):
        PrefPanel.__init__(self, app, dlg)
        grid = wal.GridPanel(self, rows=2, cols=3, hgap=5, vgap=5)

        grid.pack(wal.Label(grid, _('Constrain angle:')))
        self.constrain_angle = wal.IntSpin(
            grid, config.curve_fixed_angle, range_val=(1, 90)
        )
        grid.pack(self.constrain_angle, fill=True)
        grid.pack(wal.Label(grid, _('degrees')))

        grid.pack(wal.Label(grid, _('Node size:')))
        self.node_size = wal.Combolist(grid, items=NODE_SIZE_SCHEME)
        try:
            node_size_idx = NODE_SIZE.index(config.point_size)
        except ValueError:
            node_size_idx = 0
        self.node_size.set_active(node_size_idx)
        grid.pack(self.node_size)

        self.pack(grid, align_center=False, fill=True, padding=5)
        self.built = True

    def apply_changes(self):
        config.curve_fixed_angle = self.constrain_angle.get_value()

        node_size_idx = self.node_size.get_active()
        point_size = NODE_SIZE[node_size_idx]
        config.point_size = point_size
        config.curve_start_point_size = point_size
        config.curve_point_size = point_size
        config.curve_last_point_size = point_size
        config.control_point_size = point_size
        config.rect_midpoint_size = point_size
        config.rect_point_size = point_size
        config.ellipse_start_point_size = point_size
        config.ellipse_end_point_size = point_size
        config.polygon_point_size = point_size
        config.text_point_size = point_size
        config.gradient_vector_point_size = point_size

        config.sel_marker_size = point_size + 2
        config.curve_new_point_size = point_size + 2
        config.curve_active_point_size = point_size + 2

    def restore_defaults(self):
        defaults = config.get_defaults()
        self.constrain_angle.set_value(defaults['curve_fixed_angle'])
        self.node_size.set_active(0)

    def build(self):
        self.built = True
