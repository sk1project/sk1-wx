# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

from copy import deepcopy
import wal

from uc2 import uc2const
from uc2.formats.sk2 import sk2_const

from sk1 import _
from sk1.dialogs.colordlg import change_color_dlg
from sk1.resources import icons, get_icon

from colorctrls import SwatchCanvas, AlphaColorSwatch

CMYK_PALETTE = [
[[0.0, [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 1.0], 1.0, 'Black']],
[1.0, [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 1.0], 0.0, 'Black']]],
[[0.0, [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 1.0], 1.0, 'Black']],
[1.0, [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 0.0], 1.0, 'White']]],
[[0.0, [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 0.0], 0.0, 'White']],
[1.0, [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 0.0], 1.0, 'White']]],
]

RGB_PALETTE = [
[[0.0, [uc2const.COLOR_RGB, [0.0, 0.0, 0.0], 1.0, 'Black']],
[1.0, [uc2const.COLOR_RGB, [0.0, 0.0, 0.0], 0.0, 'Black']]],
[[0.0, [uc2const.COLOR_RGB, [0.0, 0.0, 0.0], 1.0, 'Black']],
[1.0, [uc2const.COLOR_RGB, [1.0, 1.0, 1.0], 1.0, 'White']]],
[[0.0, [uc2const.COLOR_RGB, [1.0, 1.0, 1.0], 0.0, 'White']],
[1.0, [uc2const.COLOR_RGB, [1.0, 1.0, 1.0], 1.0, 'White']]],
]

GRAY_PALETTE = [
[[0.0, [uc2const.COLOR_GRAY, [0.0, ], 1.0, 'Black']],
[1.0, [uc2const.COLOR_GRAY, [0.0, ], 0.0, 'Black']]],
[[0.0, [uc2const.COLOR_GRAY, [0.0, ], 1.0, 'Black']],
[1.0, [uc2const.COLOR_GRAY, [1.0, ], 1.0, 'White']]],
[[0.0, [uc2const.COLOR_GRAY, [1.0, ], 0.0, 'White']],
[1.0, [uc2const.COLOR_GRAY, [1.0, ], 1.0, 'White']]],
]

PALETTES = {
uc2const.COLOR_CMYK:CMYK_PALETTE,
uc2const.COLOR_RGB:RGB_PALETTE,
uc2const.COLOR_GRAY:GRAY_PALETTE,
}

DEFAULT_STOPS = [[0.0, [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 1.0], 1.0, 'Black']],
[1.0, [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 1.0], 0.0, 'Black']]]

class GradientPaletteSwatch(wal.VPanel, SwatchCanvas):

	callback = None

	def __init__(self, parent, cms, stops, size=(80, 20), onclick=None):
		self.color = None
		self.cms = cms
		wal.VPanel.__init__(self, parent)
		SwatchCanvas.__init__(self)
		self.pack(size)
		if onclick: self.callback = onclick
		self.set_stops(stops)

	def set_stops(self, stops):
		self.stops = stops
		self.fill = [0, sk2_const.FILL_GRADIENT,
				[sk2_const.GRADIENT_LINEAR, [], self.stops]]
		self.refresh()

	def mouse_left_up(self, point):
		if self.callback: self.callback(deepcopy(self.stops))

class GradientMiniPalette(wal.VPanel):

	callback = None
	cells = []

	def __init__(self, parent, cms, stops=[], onclick=None):
		wal.VPanel.__init__(self, parent)
		self.set_bg(wal.BLACK)
		grid = wal.GridPanel(parent, 2, 3, 1, 1)
		grid.set_bg(wal.BLACK)
		self.cells = []

		for item in range(6):
			self.cells.append(GradientPaletteSwatch(grid, cms,
							deepcopy(DEFAULT_STOPS), onclick=self.on_click))
			grid.pack(self.cells[-1])
		self.pack(grid, padding_all=1)
		if onclick: self.callback = onclick
		self.set_stops(stops)

	def set_stops(self, stops=[]):
		if stops:
			palette = PALETTES[stops[0][1][0]]
			for item in palette:
				self.cells[palette.index(item)].set_stops(item)
			clr1 = deepcopy(stops[0][1])
			clr1[2] = 1.0
			clr1a = deepcopy(stops[0][1])
			clr1a[2] = 0.0
			clr2 = deepcopy(stops[-1][1])
			clr2[2] = 1.0
			clr2a = deepcopy(stops[-1][1])
			clr2a[2] = 0.0
			stops = [
				[[0.0, clr1], [1.0, clr1a]],
				[[0.0, clr1], [1.0, clr2]],
				[[0.0, clr2a], [1.0, clr2]],
				]
			for item in stops:
				self.cells[stops.index(item) + 3].set_stops(item)

	def on_click(self, stops):
		if self.callback: self.callback(stops)

class StopPanel(wal.LabeledPanel):

	dlg = None
	cms = None
	stops = None
	selected_stop = 0
	pos_callback = None
	color_callback = None

	def __init__(self, parent, dlg, cms, stops, sel_stop=0, onposition=None,
				oncolor=None):
		self.dlg = dlg
		self.cms = cms
		self.stops = stops
		self.selected_stop = sel_stop
		self.pos_callback = onposition
		self.color_callback = oncolor
		wal.LabeledPanel.__init__(self, parent, text=_('Gradient stop'))
		grid = wal.GridPanel(self, cols=3, vgap=5, hgap=5)

		grid.pack(wal.Label(grid, _('Color value:')))

		spanel = wal.HPanel(grid)
		clr = self.stops[self.selected_stop][1]
		self.swatch = AlphaColorSwatch(spanel, self.cms, clr, (40, 20), 'news',
									onclick=self.edit_color)
		spanel.pack(self.swatch)

		txt = _('Change stop color')
		spanel.pack(wal.ImageButton(spanel, icons.PD_EDIT, wal.SIZE_16,
				tooltip=txt, flat=False, onclick=self.edit_color), padding=5)

		grid.pack(spanel)
		grid.pack((1, 1))

		grid.pack(wal.Label(grid, _('Position:')))
		self.position = wal.FloatSpin(grid, range_val=(0.0, 100.0), step=1.0,
							onchange=self.pos_changed, onenter=self.pos_changed)
		grid.pack(self.position)
		grid.pack(wal.Label(grid, '%'))
		self.pack(grid, align_center=False, padding_all=10)

	def edit_color(self):
		clr = self.stops[self.selected_stop][1]
		ret = change_color_dlg(self.dlg, self.cms, clr)
		if ret:
			self.stops[self.selected_stop][1] = ret
			self.update()
			if self.color_callback:self.color_callback()

	def pos_changed(self):
		if self.pos_callback:
			pos = self.position.get_value() / 100.0
			self.pos_callback(self.selected_stop, pos)

	def set_selected_stop(self, index):
		self.selected_stop = index
		self.update()

	def set_stops(self, stops):
		self.stops = stops
		self.set_selected_stop(0)

	def update(self):
		last_indx = len(self.stops) - 1
		self.swatch.set_color(self.stops[self.selected_stop][1])
		self.position.set_value(self.stops[self.selected_stop][0] * 100.0)
		self.position.set_enable(not self.selected_stop in [0, last_indx])

class StopsEditor(wal.VPanel, wal.SensitiveCanvas):

	stops = []
	selected_stop = 0
	bmp_knob = None
	bmp_stop = None
	bmp_knob_s = None
	bmp_stop_s = None
	callback = None
	callback2 = None
	pick_flag = False

	def __init__(self, parent, stops, size=(418, 10), onchange=None,
				onmove=None):
		self.stops = stops
		self.callback = onchange
		self.callback2 = onmove
		wal.VPanel.__init__(self, parent)
		wal.SensitiveCanvas.__init__(self, True)
		self.pack(size)
		self.bmp_knob = get_icon(icons.SLIDER_KNOB, size=wal.DEF_SIZE)
		self.bmp_knob_s = get_icon(icons.SLIDER_KNOB_SEL, size=wal.DEF_SIZE)
		self.bmp_stop = get_icon(icons.SLIDER_STOP, size=wal.DEF_SIZE)
		self.bmp_stop_s = get_icon(icons.SLIDER_STOP_SEL, size=wal.DEF_SIZE)

	def paint(self):
		self.draw_stops()
		self.draw_selected_stop()

	def draw_stops(self):
		w = self.get_size()[0]
		self.draw_bitmap(self.bmp_stop, 0, 0)
		self.draw_bitmap(self.bmp_stop, w - 5, 0)
		if len(self.stops) > 2:
			for stop in self.stops[1:-1]:
				pos = int(stop[0] * 400 + 6)
				self.draw_bitmap(self.bmp_knob, pos, 0)

	def draw_selected_stop(self):
		w = self.get_size()[0]
		if self.selected_stop == 0:
			self.draw_bitmap(self.bmp_stop_s, 0, 0)
		elif self.selected_stop == len(self.stops) - 1:
			self.draw_bitmap(self.bmp_stop_s, w - 5, 0)
		else:
			stop = self.stops[self.selected_stop]
			pos = int(stop[0] * 400 + 6)
			self.draw_bitmap(self.bmp_knob_s, pos, 0)

	def set_stops(self, stops):
		self.stops = stops
		self.refresh()

	def set_selected_stop(self, index):
		self.selected_stop = index
		self.refresh()

	def change_selected_stop(self, index):
		if self.callback:self.callback(index)

	def check_stop_point(self, val):
		ret = None
		w = self.get_size()[0] - 12
		index = 1
		for stop in self.stops[1:-1]:
			if val > w * stop[0] - 4 and val < w * stop[0] + 4:
				ret = index
			index += 1
		return ret

	def mouse_move(self, point):
		if self.pick_flag:
			if self.callback2:
				w = self.get_size()[0]
				pos = point[0] - 9
				if pos > w - 18:pos = w - 18
				if pos < 0:pos = 0
				pos /= (w - 18) * 1.0
				self.callback2(self.selected_stop, pos)

	def mouse_left_up(self, point):
		self.pick_flag = False

	def mouse_left_down(self, point):
		x = point[0]
		w = self.get_size()[0]
		if x < 9:
			self.change_selected_stop(0)
		elif x > w - 8:
			self.change_selected_stop(len(self.stops) - 1)
		else:
			index = self.check_stop_point(x - 8)
			if not index is None:
				self.change_selected_stop(index)
				self.pick_flag = True


class GradientViewer(wal.VPanel, SwatchCanvas):

	color = None
	callback = None

	def __init__(self, parent, cms, stops, size=(402, 40), border='news',
				onclick=None):
		self.cms = cms
		wal.VPanel.__init__(self, parent)
		SwatchCanvas.__init__(self, border)
		self.pack(size)
		self.fill = [0, sk2_const.FILL_GRADIENT,
					[sk2_const.GRADIENT_LINEAR, [], []]]
		self.set_stops(stops)
		if onclick: self.callback = onclick

	def mouse_left_dclick(self, point):
		x = point[0]
		if x > 400:x = 400
		if x: x -= 1
		if self.callback: self.callback(x / 400.0)

	def set_stops(self, stops):
		self.fill[2][2] = stops
		self.refresh()

class GradientEditor(wal.VPanel):

	dlg = None
	stops = None
	callback = None
	selected_stop = 0

	def __init__(self, parent, dlg, cms, stops, onchange=None):
		self.dlg = dlg
		self.cms = cms
		self.stops = deepcopy(stops)
		if onchange: self.callback = onchange
		wal.VPanel.__init__(self, parent)
		self.pack((5, 5))
		self.viewer = GradientViewer(self, self.cms, self.stops,
									onclick=self.insert_stop)
		self.pack(self.viewer)
		self.stop_editor = StopsEditor(self, self.stops,
									onchange=self.set_selected_stop,
									onmove=self.change_stop_position)
		self.pack(self.stop_editor)
		self.pack((5, 5))

		hpanel = wal.HPanel(self)
		self.stop_panel = StopPanel(hpanel, self.dlg, self.cms, self.stops,
								onposition=self.change_stop_position,
								oncolor=self.update_colors)
		hpanel.pack((5, 5))
		hpanel.pack(self.stop_panel)
		hpanel.pack((5, 5))

		vpanel = wal.VPanel(hpanel)
		selpanel = wal.HPanel(vpanel)

		txt = _('Select first stop')
		self.go_first = wal.ImageButton(selpanel, icons.PD_GOTO_FIRST,
				wal.SIZE_16, tooltip=txt, flat=False, onclick=self.select_first)
		selpanel.pack(self.go_first, padding=5)

		txt = _('Select previous stop')
		self.go_prev = wal.ImageButton(selpanel, icons.PD_GO_BACK,
				wal.SIZE_16, tooltip=txt, flat=False, onclick=self.select_prev)
		selpanel.pack(self.go_prev, padding=5)

		txt = _('Select next stop')
		self.go_next = wal.ImageButton(selpanel, icons.PD_GO_FORWARD,
				wal.SIZE_16, tooltip=txt, flat=False, onclick=self.select_next)
		selpanel.pack(self.go_next, padding=5)

		txt = _('Select last stop')
		self.go_last = wal.ImageButton(selpanel, icons.PD_GOTO_LAST,
				wal.SIZE_16, tooltip=txt, flat=False, onclick=self.select_last)
		selpanel.pack(self.go_last, padding=5)

		vpanel.pack(selpanel)

		bpanel = wal.HPanel(vpanel)

		txt = _('Add stop')
		self.add_button = wal.ImageButton(bpanel, icons.PD_ADD,
			wal.SIZE_16, tooltip=txt, flat=False, onclick=self.add_stop)
		bpanel.pack(self.add_button, padding=5)

		txt = _('Delete selected stop')
		self.del_button = wal.ImageButton(bpanel, icons.PD_REMOVE,
			wal.SIZE_16, tooltip=txt, flat=False, onclick=self.delete_selected)
		bpanel.pack(self.del_button)

		txt = _('Reverse gradient')
		bpanel.pack(wal.Button(vpanel, _('Reverse'), tooltip=txt,
							onclick=self.reverse_gradient), padding=15)

		vpanel.pack(bpanel, padding=5)

		txt = _('Keep gradient vector')
		self.keep_vector = wal.Checkbox(vpanel, txt, True)
		vpanel.pack(self.keep_vector)

		hpanel.pack(vpanel, fill=True, expand=True, padding=5)

		self.pack(hpanel, fill=True)

		self.update()

	def use_vector(self):
		return self.keep_vector.get_value()

	def add_stop(self):
		indx = self.selected_stop
		if indx < len(self.stops) - 1:
			start = self.stops[indx][0]
			end = self.stops[indx + 1][0]
		else:
			start = self.stops[indx - 1][0]
			end = self.stops[indx][0]
		pos = start + (end - start) / 2.0
		self.insert_stop(pos)

	def delete_selected(self):
		indx = self.selected_stop
		self.stops = self.stops[:indx] + self.stops[indx + 1:]
		if self.callback: self.callback()
		self.selected_stop = indx
		self.update()

	def reverse_gradient(self):
		self.stops.reverse()
		for item in self.stops:
			item[0] = 1.0 - item[0]
		indx = len(self.stops) - 1 - self.selected_stop
		if self.callback: self.callback()
		self.selected_stop = indx
		self.update()

	def select_first(self):
		self.set_selected_stop(0)

	def select_prev(self):
		self.set_selected_stop(self.selected_stop - 1)

	def select_next(self):
		self.set_selected_stop(self.selected_stop + 1)

	def select_last(self):
		self.set_selected_stop(len(self.stops) - 1)

	def set_selected_stop(self, index):
		self.selected_stop = index
		self.update()

	def set_stops(self, stops):
		self.stops = deepcopy(stops)
		self.selected_stop = 0
		self.update()

	def get_stops(self):
		return deepcopy(self.stops)

	def change_stop_position(self, index, pos):
		stops = self.stops[:index] + self.stops[index + 1:]
		stop = self.stops[index]
		stop[0] = pos

		before = 0
		after = len(stops) - 1
		if not pos == 1.0:
			index = -1
			for item in stops:
				index += 1
				if item[0] <= pos:
					before = index
			after = 1 + before
		else:
			before = after - 1
		stops.insert(after, stop)
		self.stops = stops
		if self.callback: self.callback()
		self.selected_stop = after
		self.update()

	def insert_stop(self, pos):
		before = 0
		after = len(self.stops) - 1
		if not pos == 1.0:
			index = -1
			for stop in self.stops:
				index += 1
				if stop[0] <= pos:
					before = index
			after = 1 + before
		else:
			before = after - 1
		c0 = self.stops[before][0]
		c1 = self.stops[after][0]
		if c1 - c0:
			coef = (pos - c0) / (c1 - c0)
			clr = self.cms.mix_colors(self.stops[before][1],
								self.stops[after][1], coef)
		else:
			clr = deepcopy(self.stops[before][1])
		self.stops.insert(after, [pos, clr])
		if self.callback: self.callback()
		self.selected_stop = after
		self.update()

	def update_colors(self):
		if self.callback: self.callback()
		self.update()

	def update(self):
		last_indx = len(self.stops) - 1
		self.viewer.set_stops(self.stops)
		self.stop_editor.set_stops(self.stops)
		self.stop_editor.set_selected_stop(self.selected_stop)
		self.stop_panel.set_stops(self.stops)
		self.stop_panel.set_selected_stop(self.selected_stop)
		self.go_first.set_enable(self.selected_stop > 0)
		self.go_prev.set_enable(self.selected_stop > 0)
		self.go_next.set_enable(self.selected_stop < last_indx)
		self.go_last.set_enable(self.selected_stop < last_indx)
		self.del_button.set_enable(not self.selected_stop in (0, last_indx))

