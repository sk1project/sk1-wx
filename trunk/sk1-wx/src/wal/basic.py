# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013 by Igor E. Novikov
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
#
#   MacOS X env: export VERSIONER_PYTHON_PREFER_32_BIT=yes

import wx, const

from generic import Widget
from const import FONT_SIZE, DEF_SIZE


class Application(wx.App):

	app_name = None

	mw = None
	mdi = None
	actions = []

	def __init__(self, name='', redirect=False):
		wx.App.__init__(self, redirect=redirect)
		if name:
			self.set_app_name(name)
		const.set_ui_colors(const.UI_COLORS)
		self._set_font_size()

	def _set_font_size(self):
		dc = wx.MemoryDC()
		dc.SetFont(wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT))
		FONT_SIZE[0] = dc.GetTextExtent('D')[0]
		FONT_SIZE[1] = dc.GetCharHeight()

	def set_app_name(self, name):
		self.app_name = name
		self.SetAppName(name)
		self.SetClassName(name)

	def update_actions(self):
		for item in self.actions.keys():
			self.actions[item].update()

	def call_after(self, *args):pass

	def run(self):
		if self.mw:
			self.SetTopWindow(self.mw)
			self.mw.build()
			if self.mw.maximized: self.mw.Maximize()
			self.mw.Show(True)
			self.mdi = self.mw.mdi
			if self.actions:self.update_actions()
			wx.CallAfter(self.call_after)
			self.MainLoop()
		else:
			raise RuntimeError, 'Main window is not defined!'

class MainWindow(wx.Frame):

	mdi = None
	maximized = False

	def __init__(self, title='Frame', size=(100, 100), orientation=wx.VERTICAL,
				maximized=False, on_close=None):
		self.maximized = maximized

		wx.Frame.__init__(self, None, wx.ID_ANY, title, pos=DEF_SIZE, size=size,
						name=title)
		self.orientation = orientation
		self.Centre()
		self.box = wx.BoxSizer(orientation)
		self.SetSizer(self.box)
		self.set_title(title)
		if on_close: self.Bind(wx.EVT_CLOSE, on_close, self)

	def build(self):pass

	def layout(self): self.Layout()

	def add(self, *args, **kw):
		"""Arguments: object, expandable (0 or 1), flag, border"""
		self.box.Add(*args, **kw)

	def pack(self, obj, expand=False, fill=False,
			padding=0, start_padding=0, end_padding=0):
		if self.orientation == wx.VERTICAL:
			if expand:expand = 1
			else: expand = 0
			flags = wx.ALIGN_TOP | wx.ALIGN_CENTER_HORIZONTAL
			if padding:
				flags = flags | wx.TOP | wx.BOTTOM
			elif start_padding:
				flags = flags | wx.TOP
				padding = start_padding
			elif end_padding:
				flags = flags | wx.BOTTOM
				padding = end_padding
			if fill: flags = flags | wx.EXPAND
			self.box.Add(obj, expand, flags, padding)
		else:
			if expand:expand = 1
			else: expand = 0
			flags = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL
			if padding:
				flags = flags | wx.LEFT | wx.RIGHT
			elif start_padding:
				flags = flags | wx.LEFT
				padding = start_padding
			elif end_padding:
				flags = flags | wx.RIGHT
				padding = end_padding
			if fill: flags = flags | wx.EXPAND
			self.box.Add(obj, expand, flags, padding)

	def set_title(self, title):
		self.SetTitle(title)

	def set_minsize(self, w, h):
		self.SetMinSize((w, h))

	def set_icons(self, filepath):
		icons = wx.IconBundle()
		icons.AddIconFromFile(filepath, wx.BITMAP_TYPE_ANY)
		self.SetIcons(icons)

class Panel(wx.Panel, Widget):

	def __init__(self, parent):
		wx.Panel.__init__(self, parent, wx.ID_ANY)

	def set_bg(self, color):
		self.SetBackgroundColour(wx.Colour(*color))

class SizedPanel(Panel):

	panel = None

	def __init__(self, parent, orientation=wx.HORIZONTAL):
		self.parent = parent
		self.orientation = orientation
		Panel.__init__(self, parent)
		self.box = wx.BoxSizer(orientation)
		self.SetSizer(self.box)
		self.panel = self

	def add(self, *args, **kw):
		"""Arguments: object, expandable (0 or 1), flag, border"""
		obj = args[0]
		if not isinstance(obj, tuple):
			if not obj.GetParent() == self.panel:
				obj.Reparent(self.panel)
		self.box.Add(*args, **kw)

	def box_add(self, *args, **kw):
		"""Arguments: object, expandable (0 or 1), flag, border"""
		self.box.Add(*args, **kw)

	def remove(self, obj):
		self.box.Detach(obj)


class BorderedPanel(SizedPanel):
	def __init__(self, parent, orientation=wx.HORIZONTAL, border=None, space=0):
		if border is None:
			SizedPanel.__init__(self, parent, orientation)
			self.panel = self
			self.inner_box = self.box
		else:
			if orientation == wx.HORIZONTAL and border in (wx.TOP, wx.BOTTOM):
				SizedPanel.__init__(self, parent, wx.VERTICAL)
				if border == wx.TOP:
					line = wx.StaticLine(self, style=wx.HORIZONTAL)
					self.add(line, 0, wx.ALL | wx.EXPAND)
				box = wx.BoxSizer(wx.HORIZONTAL)
				self.box.Add(box, 0, wx.ALL | wx.EXPAND)
				self.inner_box = self.box
				self.box = box
				if border == wx.BOTTOM:
					line = wx.StaticLine(self, style=wx.HORIZONTAL)
					self.inner_box.Add(line, 0, wx.ALL | wx.EXPAND)
			elif orientation == wx.HORIZONTAL and border in (wx.LEFT, wx.RIGHT):
				SizedPanel.__init__(self, parent, wx.HORIZONTAL)
				if border == wx.LEFT:
					line = wx.StaticLine(self, style=wx.VERTICAL)
					self.add(line, 0, wx.ALL | wx.EXPAND)
				box = wx.BoxSizer(wx.HORIZONTAL)
				self.box.Add(box, 0, wx.ALL | wx.EXPAND)
				self.inner_box = self.box
				self.box = box
				if border == wx.RIGHT:
					line = wx.StaticLine(self, style=wx.VERTICAL)
					self.inner_box.Add(line, 0, wx.ALL | wx.EXPAND)
			elif orientation == wx.VERTICAL and border in (wx.TOP, wx.BOTTOM):
				SizedPanel.__init__(self, parent, wx.VERTICAL)
				if border == wx.TOP:
					line = wx.StaticLine(self, style=wx.HORIZONTAL)
					self.add(line, 0, wx.ALL | wx.EXPAND)
				box = wx.BoxSizer(wx.VERTICAL)
				self.box.Add(box, 0, wx.ALL | wx.EXPAND)
				self.inner_box = self.box
				self.box = box
				if border == wx.BOTTOM:
					line = wx.StaticLine(self, style=wx.HORIZONTAL)
					self.inner_box.Add(line, 0, wx.ALL | wx.EXPAND)
			else:
				SizedPanel.__init__(self, parent, wx.HORIZONTAL)
				if border == wx.LEFT:
					line = wx.StaticLine(self, style=wx.VERTICAL)
					self.add(line, 0, wx.ALL | wx.EXPAND)
				box = wx.BoxSizer(wx.VERTICAL)
				self.box.Add(box, 0, wx.ALL | wx.EXPAND)
				self.inner_box = self.box
				self.box = box
				if border == wx.RIGHT:
					line = wx.StaticLine(self, style=wx.VERTICAL)
					self.inner_box.Add(line, 0, wx.ALL | wx.EXPAND)
			self.panel = self

class HPanel(SizedPanel):
	def __init__(self, parent, border=None, space=0):
		SizedPanel.__init__(self, parent, wx.HORIZONTAL)

	def pack(self, obj, expand=False, fill=False,
			padding=0, start_padding=0, end_padding=0):
		if expand:expand = 1
		else: expand = 0
		flags = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL
		if padding:
			flags = flags | wx.LEFT | wx.RIGHT
		elif start_padding:
			flags = flags | wx.LEFT
			padding = start_padding
		elif end_padding:
			flags = flags | wx.RIGHT
			padding = end_padding
		if fill: flags = flags | wx.EXPAND
		self.box.Add(obj, expand, flags, padding)

class VPanel(SizedPanel):
	def __init__(self, parent, border=None, space=0):
		SizedPanel.__init__(self, parent, wx.VERTICAL)

	def pack(self, obj, expand=False, fill=False,
			padding=0, start_padding=0, end_padding=0):
		if expand:expand = 1
		else: expand = 0
		flags = wx.ALIGN_TOP | wx.ALIGN_CENTER_HORIZONTAL
		if padding:
			flags = flags | wx.TOP | wx.BOTTOM
		elif start_padding:
			flags = flags | wx.TOP
			padding = start_padding
		elif end_padding:
			flags = flags | wx.BOTTOM
			padding = end_padding
		if fill: flags = flags | wx.EXPAND
		self.box.Add(obj, expand, flags, padding)


class LabeledPanel(wx.StaticBox, Widget):

	sizer = None

	def __init__(self, parent, text='', size=DEF_SIZE,
				 orientation=wx.VERTICAL):
		wx.StaticBox.__init__(self, parent, wx.ID_ANY, text,
							pos=DEF_SIZE, size=size)
		self.box = wx.StaticBoxSizer(self, orientation)

	def add(self, *args, **kw):
		"""Arguments: object, expandable (0 or 1), flag, border"""
		self.box.Add(*args, **kw)



