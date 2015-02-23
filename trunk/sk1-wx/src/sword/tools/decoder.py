# -*- coding: utf-8 -*-
#
#	Copyright (C) 2012 by Igor E. Novikov
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

import gtk

from sword import _, events
from sword.widgets.captions import TabIconCaption
from sword.models.decoderlist import DecoderListModel

class Decoder(gtk.VBox):

	name = "Decoder"
	caption = _("Decoder")
	caption_label = None
	data = ''

	def __init__(self, app):

		gtk.VBox.__init__(self)
		self.app = app
		self.caption_label = TabIconCaption(gtk.STOCK_INDEX, self.caption)
		self.data = ''

		spacer = gtk.VBox()
		self.add(spacer)
		self.set_border_width(5)

		nav_panel = gtk.HBox()
		nav_panel.set_border_width(0)
		spacer.pack_start(nav_panel, False, False)

		#---Panel internal content---

		self.dec_box = DecoderTab(app)
		spacer.pack_start(self.dec_box, False, False)

		self.be_check = gtk.CheckButton(label=_('Big Endian values'))
		self.be_check.set_active(False)
		self.be_check.connect('clicked', self.change_be_check)
		spacer.pack_start(self.be_check, False, False)

		calc_frame = HexDecCalc()
		spacer.pack_start(calc_frame, False, False)
		#----------------------------

		self.show_all()
		events.connect(events.BIN_SELECTION, self.get_selection)

	def get_selection(self, *args):
		self.data = args[0][0]
		self.change_be_check()

	def change_be_check(self, *args):
		self.dec_box.update_data(self.data, self.be_check.get_active())


class DecoderTab(gtk.ScrolledWindow):

	big_endian = False

	def __init__(self, app):
		gtk.ScrolledWindow.__init__(self)
		self.app = app

		self.treeview = gtk.TreeView()

		self.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_NEVER)

		listmodel = DecoderListModel()

		self.column = gtk.TreeViewColumn()
		self.column.set_title(_('Type'))
		render_text = gtk.CellRendererText()
		self.column.pack_start(render_text, expand=True)
		self.column.add_attribute(render_text, 'text', 0)
		self.treeview.append_column(self.column)

		self.column1 = gtk.TreeViewColumn()
		self.column1.set_title(_('Value'))
		render_text = gtk.CellRendererText()
		self.column1.pack_start(render_text, expand=True)
		self.column1.add_attribute(render_text, 'text', 1)
		self.treeview.append_column(self.column1)

		self.add(self.treeview)

		self.treeview.set_model(listmodel)
		self.treeview.set_rules_hint(True)
		self.show_all()
		self.treeview.expand_all()

	def update_data(self, data='', flag=False):
		listmodel = DecoderListModel(data, flag)
		self.treeview.set_model(listmodel)


def hex_only_chars(txt):
	res = ''
	for char in txt:
		if char in '0123456789abcdef':
			res += char
	return res

def dec_only_chars(txt):
	res = ''
	for char in txt:
		if char in '0123456789':
			res += char
	return res


class HexDecCalc(gtk.Frame):

	caption = _("HEX <> DEC")
	hex_flag = False
	dec_flag = False

	def __init__(self):
		gtk.Frame.__init__(self, self.caption)

		self.set_border_width(5)

		tab = gtk.Table(2, 2, False)
		tab.set_border_width(5)
		tab.set_row_spacings(10)
		tab.set_col_spacings(10)
		self.add(tab)

		label = gtk.Label(_('Hex:'))
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 0, 1, gtk.FILL , gtk.SHRINK)

		self.hex_value = gtk.Entry()
		self.hex_value.set_width_chars(15)
		self.hex_value.set_text('0')
		tab.attach(self.hex_value, 1, 2, 0, 1, gtk.FILL | gtk.EXPAND, gtk.SHRINK)
		self.hex_value.connect('key-release-event', self.hex_changed)

		label = gtk.Label(_('Dec:'))
		label.set_alignment(0, 0.5)
		tab.attach(label, 0, 1, 1, 2, gtk.FILL , gtk.SHRINK)

		self.dec_value = gtk.Entry()
		self.dec_value.set_width_chars(15)
		self.dec_value.set_text('0')
		tab.attach(self.dec_value, 1, 2, 1, 2, gtk.FILL | gtk.EXPAND, gtk.SHRINK)
		self.dec_value.connect('key-release-event', self.dec_changed)

	def hex_changed(self, *ags):
		if self.hex_flag:
			self.hex_flag = False
			return
		txt = hex_only_chars(self.hex_value.get_text().lower())
		if not txt:txt = '0'
		if not txt == self.hex_value.get_text():
			self.change_hex(txt)
		val = int('0x' + txt, 16)
		self.change_dec('%i' % (val))

	def change_hex(self, txt):
		self.hex_flag = True
		self.hex_value.set_text(txt)

	def dec_changed(self, *args):
		if self.dec_flag:
			self.dec_flag = False
			return
		txt = dec_only_chars(self.dec_value.get_text())
		if not txt:txt = '0'
		if not txt == self.dec_value.get_text():
			self.change_dec(txt)
		val = int(txt)
		self.change_hex('%x' % (val))

	def change_dec(self, txt):
		self.dec_flag = True
		self.dec_value.set_text(txt)
