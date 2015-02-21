# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
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

import sys
import wx

from uc2 import events

class ProgressDialog(wx.ProgressDialog):

	caption = ''
	result = None
	dlg = None
	error_info = None


	def __init__(self, caption, parent):
		self.caption = caption
		self.parent = parent

	def run(self, executable, args, save_result=True):
		events.connect(events.FILTER_INFO, self._listener)
		self.dlg = wx.ProgressDialog(self.caption,
						' ' * 80,
						parent=self.parent,
						style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
						)

		try:
			if save_result: self.result = executable(*args)
			else: executable(*args)
		except:
			self.result = None
			self.error_info = sys.exc_info()
			return False
		return True

	def _listener(self, *args):
		val = round(args[0][1], 2)
		info = args[0][0]
		self.dlg.Update(int(val * 100.0), info)

	def destroy(self):
		self.dlg.Destroy()
		events.disconnect(events.FILTER_INFO, self._listener)
