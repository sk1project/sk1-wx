# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013-2015 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wx

from generic import Widget, DataWidget, RangeDataWidget
import const
from const import DEF_SIZE
from basic import HPanel

class Bitmap(wx.StaticBitmap, Widget):

	def __init__(self, parent, bitmap, on_left_click=None, on_right_click=None):
		wx.StaticBitmap.__init__(self, parent, wx.ID_ANY, bitmap)
		if on_left_click:
			self.Bind(wx.EVT_LEFT_UP, on_left_click, self)
		if on_right_click:
			self.Bind(wx.EVT_RIGHT_UP, on_right_click, self)

	def set_bitmap(self, bmp):
		self.SetBitmap(bmp)

class Notebook(wx.Notebook, Widget):

	childs = []

	def __init__(self, parent):
		self.childs = []
		wx.Notebook.__init__(self, parent, wx.ID_ANY)

	def add_page(self, page, title):
		self.childs.append(page)
		self.AddPage(page, title)

	def remove_page(self, page):
		index = self.childs.index(page)
		self.childs.remove(page)
		self.RemovePage(index)


class VLine(wx.StaticLine, Widget):
	def __init__(self, parent):
		wx.StaticLine.__init__(self, parent, style=wx.VERTICAL)


class HLine(wx.StaticLine, Widget):
	def __init__(self, parent):
		wx.StaticLine.__init__(self, parent, style=wx.HORIZONTAL)


class Label(wx.StaticText, Widget):

	def __init__(self, parent, text='', fontbold=False, fontsize=0, fg=()):
		wx.StaticText.__init__(self, parent, wx.ID_ANY, text)
		font = self.GetFont()
		if fontbold:
			font.SetWeight(wx.FONTWEIGHT_BOLD)
		if fontsize:
			if isinstance(fontsize, str):
				sz = int(fontsize)
				if font.IsUsingSizeInPixels():
					font.SetPixelSize((0, sz))
				else:
					font.SetPointSize(sz)
			else:
				if font.IsUsingSizeInPixels():
					sz = font.GetPixelSize()[1] + fontsize
					font.SetPixelSize((0, sz))
				else:
					sz = font.GetPointSize() + fontsize
					font.SetPointSize(sz)
		self.SetFont(font)
		if fg:
			self.SetForegroundColour(wx.Colour(*fg))

	def set_text(self, text):
		self.SetLabel(text)


class HtmlLabel(wx.HyperlinkCtrl, Widget):
	def __init__(self, parent, text, url=''):
		if not url:url = text
		wx.HyperlinkCtrl.__init__(self, parent, wx.ID_ANY, text, url)


class Button(wx.Button, Widget):

	callback = None

	def __init__(self, parent, text, size=DEF_SIZE,
				onclick=None, tooltip='', default=False, pid=wx.ID_ANY):
		wx.Button.__init__(self, parent, pid, text, size=size)
		if default: self.SetDefault()
		if onclick:
			self.callback = onclick
			self.Bind(wx.EVT_BUTTON, self.on_click, self)
		if tooltip: self.SetToolTipString(tooltip)

	def set_default(self):self.SetDefault()

	def on_click(self, event):
		if self.callback: self.callback()


class Checkbox(wx.CheckBox, DataWidget):

	callback = None

	def __init__(self, parent, text='', value=False, onclick=None, right=False):
		style = 0
		if right:style = wx.ALIGN_RIGHT
		wx.CheckBox.__init__(self, parent, wx.ID_ANY, text, style=style)
		if value: self.SetValue(value)
		if onclick:
			self.callback = onclick
			self.Bind(wx.EVT_CHECKBOX, self.on_click, self)

	def set_value(self, val, action=True):
		self.SetValue(val)
		if action:self.on_click()

	def on_click(self, event=None):
		if self.callback:self.callback()


class Radiobutton(wx.RadioButton, DataWidget):

	callback = None

	def __init__(self, parent, text='', onclick=None, group=False):
		style = 0
		if group:style = wx.RB_GROUP
		wx.RadioButton.__init__(self, parent, wx.ID_ANY, text, style=style)
		if onclick:
			self.callback = onclick
			self.Bind(wx.wx.EVT_RADIOBUTTON, self.on_click, self)

	def on_click(self, event):
		if self.callback: self.callback()


class Combolist(wx.Choice, Widget):

	items = []
	callback = None

	def __init__(self, parent, size=DEF_SIZE, width=0, items=[], onchange=None):
		self.items = []
		if items: self.items = items
		size = self._set_width(size, width)
		wx.Choice.__init__(self, parent, wx.ID_ANY, size, choices=self.items)
		if onchange:
			self.callback = onchange
			self.Bind(wx.EVT_CHOICE, self.on_change, self)

	def on_change(self, event):
		if self.callback: self.callback()

	def set_items(self, items):
		self.SetItems(items)

	def set_selection(self, index):
		if index < self.GetCount(): self.SetSelection(index)

	def get_selection(self):
		return self.GetSelection()

	def set_active(self, index):
		self.set_selection(index)

	def get_active(self):
		return self.get_selection()

class Combobox(wx.ComboBox, DataWidget):

	items = []
	callback = None

	def __init__(self, parent, value='', pos=(-1, 1), size=DEF_SIZE, width=0,
				items=[], onchange=None):
		self.items = []
		if items: self.items = items
		flags = wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER
		size = self._set_width(size, width)
		wx.ComboBox.__init__(self, parent, wx.ID_ANY, value, pos, size, items, flags)
		if onchange:
			self.callback = onchange
			self.Bind(wx.EVT_COMBOBOX, self.on_change, self)
			self.Bind(wx.EVT_TEXT_ENTER, self.on_change, self)

	def on_change(self, event):
		if self.callback: self.callback()

	def set_items(self, items):
		self.SetItems(items)

class Entry(wx.TextCtrl, DataWidget):

	my_changes = False
	value = ''

	def __init__(self, parent, value='', size=DEF_SIZE, width=0, onchange=None,
				multiline=False, richtext=False, onenter=None, editable=True):
		style = 0
		if multiline: style |= wx.TE_MULTILINE
		if richtext: style |= wx.TE_RICH2
		if onenter: style |= wx.TE_PROCESS_ENTER
		size = self._set_width(size, width)
		wx.TextCtrl.__init__(self, parent, wx.ID_ANY, value, size=size, style=style)
		if onchange: self.Bind(wx.EVT_TEXT, onchange, self)
		if onenter: self.Bind(wx.EVT_TEXT_ENTER, onenter, self)
		if not editable:
			self.value = value
			self.Bind(wx.EVT_TEXT, self.on_change, self)
			self.Bind(wx.EVT_TEXT_ENTER, self.on_change, self)

	def on_change(self, event):
		if self.my_changes:
			self.my_changes = False
			return
		self.my_changes = True
		self.SetValue(self.value)

	def get_value(self):
		return str(self.GetValue())


class Spin(wx.SpinCtrl, RangeDataWidget):

	callback = None

	def __init__(self, parent, value=0, range_val=(0, 1), size=DEF_SIZE, width=0,
				 onchange=None):
		self.range_val = range_val
		size = self._set_width(size, width)
		wx.SpinCtrl.__init__(self, parent, wx.ID_ANY, '', size)
		self.SetRange(*range_val)
		self.SetValue(value)
		if onchange:
			self.callback = onchange
			self.Bind(wx.EVT_SPINCTRL, onchange, self)

	def on_change(self, event):
		if self.callback: self.callback()

class SpinButton(wx.SpinButton, RangeDataWidget):

	def __init__(self, parent, value=0, range_val=(0, 10), size=DEF_SIZE,
				 onchange=None, vertical=True):
		self.range_val = range_val
		style = wx.SL_VERTICAL
		if not vertical:style = wx.SL_HORIZONTAL
		wx.SpinButton.__init__(self, parent, wx.ID_ANY, size=size, style=style)
		self.SetValue(value)
		self.SetRange(*range_val)
		if onchange:
			self.Bind(wx.EVT_SPIN, onchange, self)

class FloatSpin(wx.Panel, RangeDataWidget):

	entry = None
	sb = None
	line = None

	flag = True
	value = 0.0
	range_val = (0.0, 1.0)
	step = 0.01
	digits = 2
	callback = None
	enter_callback = None

	def __init__(self, parent, value=0.0, range_val=(0.0, 1.0), step=0.01,
				digits=2, size=DEF_SIZE, width=0, spin_overlay=True,
				onchange=None, onenter=None, check_focus=True):

		self.callback = onchange
		self.enter_callback = onenter
		if const.is_mac(): spin_overlay = False

		wx.Panel.__init__(self, parent)
		if spin_overlay:
			if const.is_gtk():
				self.entry = Entry(self, '', size=size, width=width,
						onchange=self._check_entry, onenter=self._entry_enter)
				size = (-1, self.entry.GetSize()[1])
				self.entry.SetPosition((0, 0))
				self.line = HPanel(self)
				self.sb = SpinButton(self, size=size, onchange=self._check_spin)
				w_pos = self.entry.GetSize()[0] - 5
				self.line.SetSize((1, self.sb.GetSize()[1] - 2))
				self.line.set_bg(const.UI_COLORS['dark_shadow'])
				self.line.SetPosition((w_pos - 1, 1))
				self.sb.SetPosition((w_pos, 0))
				self.SetSize((-1, self.entry.GetSize()[1]))
			elif const.is_msw():
				width += 2
				self.entry = Entry(self, '', size=size, width=width,
						onchange=self._check_entry, onenter=self._entry_enter)
				size = (-1, self.entry.GetSize()[1] - 4)
				self.sb = SpinButton(self.entry, size=size, onchange=self._check_spin)
				w_pos = self.entry.GetSize()[0] - self.sb.GetSize()[0] - 3
				self.sb.SetPosition((w_pos, -1))
		else:
			self.box = wx.BoxSizer(const.HORIZONTAL)
			self.SetSizer(self.box)
			self.entry = Entry(self, '', size=size, width=width,
						onchange=self._check_entry, onenter=self._entry_enter)
			self.box.Add(self.entry, 0, wx.ALL)
			size = (-1, self.entry.GetSize()[1])
			self.sb = SpinButton(self, size=size, onchange=self._check_spin)
			self.box.Add(self.sb, 0, wx.ALL)

		if check_focus:
			self.entry.Bind(wx.EVT_KILL_FOCUS, self._entry_lost_focus, self.entry)

		self.set_step(step)
		self.set_range(range_val)
		self._set_digits(digits)
		self._set_value(value)
		self.flag = False
		self.Fit()

	def set_enable(self, val):
		self.entry.Enable(val)
		self.sb.Enable(val)
		if not self.line is None:
			if val:	self.line.set_bg(const.UI_COLORS['dark_shadow'])
			else: self.line.set_bg(const.UI_COLORS['light_shadow'])

	def get_enabled(self):
		return self.entry.IsEnabled()

	def _check_spin(self, event):
		if self.flag:return
		coef = pow(10, self.digits)
		dval = float(self.sb.get_value() - int(self.value * coef))
		if not self.value == self._calc_entry():
			self._set_value(self._calc_entry())
		self.SetValue(dval * self.step + self.value)
		event.Skip()

	def _entry_enter(self, event):
		if self.flag:return
		self.SetValue(self._calc_entry())
		event.Skip()
		if not self.enter_callback is None: self.enter_callback()

	def _entry_lost_focus(self, event):
		if self.flag:return
		self.SetValue(self._calc_entry())
		event.Skip()

	def _check_entry(self, event):
		if self.flag:return
		txt = self.entry.get_value()
		res = ''
		for item in txt:
			chars = '.0123456789-+/*'
			if not self.digits: chars = '0123456789-+/*'
			if item in chars:
				res += item
		if not txt == res:
			self.flag = True
			self.entry.set_value(res)
			self.flag = False
		event.Skip()

	def _calc_entry(self):
		txt = self.entry.get_value()
		val = 0
		try:
			line = 'val=' + txt
			code = compile(line, '<string>', 'exec')
			exec code
		except:return self.value
		return val

	def _check_in_range(self, val):
		minval, maxval = self.range_val
		if val < minval:val = minval
		if val > maxval:val = maxval
		coef = pow(10, self.digits)
		val = round(val * coef) / coef
		return val

	def _set_value(self, val):
		coef = pow(10, self.digits)
		self.value = self._check_in_range(val)
		if not self.digits: self.value = int(self.value)
		self.entry.set_value(str(self.value))
		self.sb.set_value(int(self.value * coef))

	def _set_digits(self, digits):
		self.digits = digits
		self.set_range(self.range_val)

	def set_value(self, val):
		self.flag = True
		self._set_value(val)
		self.flag = False

	#----- Native API emulation
	def SetValue(self, val):
		self.flag = True
		old_value = self.value
		self._set_value(val)
		self.flag = False
		if not self.callback is None and not self.value == old_value:
			self.callback(None)

	def GetValue(self):
		if not self.value == self._calc_entry():
			self._set_value(self._calc_entry())
		return self.value

	def SetRange(self, minval, maxval):
		coef = pow(10, self.digits)
		self.range_val = (minval, maxval)
		self.sb.set_range((int(minval * coef), int(maxval * coef)))

	#----- Control API
	def set_step(self, step):
		self.step = step

	def set_digits(self, digits):
		self._set_digits(digits)
		self.SetValue(self.value)


class IntSpin(FloatSpin):

	def __init__(self, parent, value=0, range_val=(0, 1), size=DEF_SIZE,
				width=0, spin_overlay=True,
				onchange=None, onenter=None, check_focus=True):
		step = 1
		digits = 0
		FloatSpin.__init__(self, parent, value, range_val,
						step, digits, size, width, spin_overlay,
						onchange, onenter, check_focus)


class Slider(wx.Slider, RangeDataWidget):

	callback = None
	final_callback = None

	def __init__(self, parent, value=0, range_val=(1, 100),
				size=(100, -1), vertical=False, onchange=None,
				on_final_change=None):
		self.range_val = range_val
		style = 0
		if vertical:
			style |= wx.SL_VERTICAL
		else:
			style |= wx.SL_HORIZONTAL
		start, end = range_val
		wx.Slider.__init__(self, parent, wx.ID_ANY, value, start,
						end, size=size, style=style)
		if onchange:
			self.callback = onchange
			self.Bind(wx.EVT_SCROLL, self._onchange, self)
		if on_final_change:
			self.final_callback = on_final_change
			self.Bind(wx.EVT_LEFT_UP, self._on_final_change, self)
			self.Bind(wx.EVT_RIGHT_UP, self._on_final_change, self)

	def _onchange(self, event):
		if self.callback: self.callback()

	def _on_final_change(self, event):
		event.Skip()
		if self.final_callback: self.final_callback()


class Splitter(wx.SplitterWindow, Widget):

	def __init__(self, parent, live_update=True):
		style = wx.SP_NOBORDER
		if live_update: style |= wx.SP_LIVE_UPDATE
		wx.SplitterWindow.__init__(self, parent, wx.ID_ANY, style=style)

	def split_vertically(self, win1, win2, sash_pos=0):
		self.SplitVertically(win1, win2, sash_pos)

	def split_horizontally(self, win1, win2, sash_pos=0):
		self.SplitHorizontally(win1, win2, sash_pos)

	def set_min_size(self, size):
		self.SetMinimumPaneSize(size)

	def unsplit(self, remove_win=None):
		self.Unsplit(remove_win)

	def set_sash_gravity(self, val):
		self.SetSashGravity(val)

	def set_sash_position(self, val):
		self.SetSashPosition(val)

class ScrollBar(wx.ScrollBar, Widget):

	def __init__(self, parent, vertical=True):
		style = wx.SB_VERTICAL
		if not vertical: style = wx.SB_HORIZONTAL
		wx.ScrollBar.__init__(self, parent, wx.ID_ANY, style=style)

class ColorButton(wx.ColourPickerCtrl, Widget):

	callback = None

	def __init__(self, parent, color=(), onchange=None):
		if not color:
			color = const.BLACK
		else:
			color = wx.Colour(*self.val255(color))
		wx.ColourPickerCtrl.__init__(self, parent, wx.ID_ANY, color)
		if onchange:
			self.callback = onchange
			self.Bind(wx.EVT_SCROLL, self.on_change, self)

	def on_change(self, event):
		if self.callback:self.callback()

	def val255(self, vals):
		ret = []
		for item in vals: ret.append(int(item * 255))
		return tuple(ret)

	def val255_to_dec(self, vals):
		ret = []
		for item in vals: ret.append(item / 255.0)
		return tuple(ret)

	def set_value(self, color): self.SetColour(wx.Colour(*self.val255(color)))
	def get_value(self): return self.val255_to_dec(self.GetColour().Get())
