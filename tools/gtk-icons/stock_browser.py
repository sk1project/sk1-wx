#!/usr/bin/env python
'''Stock Item and Icon Browser

This source code for this demo doesn't demonstrate anything particularly
useful in applications. The purpose of the "demo" is just to provide a
handy place to browse the available stock icons and stock items.
'''
# pygtk version: Maik Hertha <maik.hertha@berlin.de>


import gobject
import gtk
import re

def id_to_macro(stock_id):
	if stock_id == '':
		return ''
	if stock_id.startswith('gtk'):
		# gtk-foo-bar -> gtk.STOCK_FOO_BAR
		macro = 'gtk.STOCK' + \
			re.sub('-([^-]+)', lambda m:('_' + m.group(1).upper()), stock_id[3:])

	else:
		# demo-gtk-logo -> DEMO_GTK_LOGO as with custom icon-factories
		macro = re.sub('([^-]+)-?', lambda m:('_' + m.group(1).upper()), stock_id)
		macro = macro[1:]  # there is a leading '_' always

	return  macro


class StockItemInfo(object):
	def __init__(self, stock_id=''):
		self.stock_id = stock_id
		self.stock_item = None
		self.small_icon = None
		self.macro = id_to_macro(stock_id)
		self.accel_str = ''

class StockItemDisplay(object):
	def __init__(self):
		self.type_label = None
		self.macro_label = None
		self.id_label = None
		self.label_accel_label = None
		self.icon_image = None


def get_largest_size(stockid):
	''' Finds the largest size at which the given image stock id is
		available. This would not be useful for a normal application.
	'''
	set = gtk.icon_factory_lookup_default(stockid)
	best_size = gtk.ICON_SIZE_INVALID
	best_pixels = 0

	sizes = set.get_sizes()
	n_sizes = len(sizes)

	i = 0
	while(i < n_sizes):
		width, height = gtk.icon_size_lookup(sizes[i])

		if(width * height > best_pixels):
			best_size = sizes[i]
			best_pixels = width * height

		i += 1

	return best_size


def macro_set_func_text(tree_column, cell, model, iter):
	info = model.get_value(iter, 0)
	cell.set_property("text", info.macro)

def id_set_func(tree_column, cell, model, iter):
	info = model.get_value(iter, 0)
	cell.set_property("text", info.stock_id)

def accel_set_func(tree_column, cell, model, iter):
	info = model.get_value(iter, 0)
	cell.set_property("text", info.accel_str)

def label_set_func(tree_column, cell, model, iter):
	info = model.get_value(iter, 0)
	cell.set_property("text", info.stock_item[1])


class StockItemAndIconBrowserDemo(gtk.Window):
	def __init__(self, parent=None):
		gtk.Window.__init__(self)
		try:
			self.set_screen(parent.get_screen())
		except AttributeError:
			self.connect('destroy', lambda * w: gtk.main_quit())

		self.set_title(self.__class__.__name__)
		self.set_default_size(-1, 500)
		self.set_border_width(8)

		hbox = gtk.HBox(False, 8)
		self.add(hbox)

		sw = gtk.ScrolledWindow()
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		hbox.pack_start(sw, False, False, 0)

		model = self.__create_model()
		treeview = gtk.TreeView(model)
		sw.add(treeview)

		column = gtk.TreeViewColumn()
		column.set_title("Macro")

		cell_renderer = gtk.CellRendererPixbuf()
		column.pack_start(cell_renderer, False)
		column.set_attributes(cell_renderer, stock_id=1)

		cell_renderer = gtk.CellRendererText()
		column.pack_start(cell_renderer, True)
		column.set_cell_data_func(cell_renderer, macro_set_func_text)

		treeview.append_column(column)

		cell_renderer = gtk.CellRendererText()
		treeview.insert_column_with_data_func(-1, "Label", cell_renderer, label_set_func)

		cell_renderer = gtk.CellRendererText()
		treeview.insert_column_with_data_func(-1, "Accel", cell_renderer, accel_set_func)

		cell_renderer = gtk.CellRendererText()
		treeview.insert_column_with_data_func(-1, "ID", cell_renderer, id_set_func)

		align = gtk.Alignment(0.5, 0.0, 0.0, 0.0)
		hbox.pack_end(align, False, False, 0)

		frame = gtk.Frame("Selected Item")
		align.add(frame)

		vbox = gtk.VBox(False, 8)
		vbox.set_border_width(4)
		frame.add(vbox)

		display = StockItemDisplay()
		treeview.set_data("stock-display", display)

		display.type_label = gtk.Label()
		display.macro_label = gtk.Label()
		display.id_label = gtk.Label()
		display.label_accel_label = gtk.Label()
		display.icon_image = gtk.Image(); # empty image

		vbox.pack_start(display.type_label, False, False, 0)
		vbox.pack_start(display.icon_image, False, False, 0)
		vbox.pack_start(display.label_accel_label, False, False, 0)
		vbox.pack_start(display.macro_label, False, False, 0)
		vbox.pack_start(display.id_label, False, False, 0)

		selection = treeview.get_selection()
		selection.set_mode(gtk.SELECTION_SINGLE)

		selection.connect("changed", self.on_selection_changed)
		self.set_position(gtk.WIN_POS_CENTER)

		self.show_all()

	def __create_model(self):
		store = gtk.ListStore(
			gobject.TYPE_PYOBJECT,
			gobject.TYPE_STRING)

		ids = gtk.stock_list_ids()
		ids.sort()

		for data in ids:
			info = StockItemInfo(stock_id=data)
			stock_item = gtk.stock_lookup(data)

			if stock_item:
				info.stock_item = stock_item
			else:
				# stock_id, label, modifier, keyval, translation_domain
				info.stock_item = ('', '', 0, 0, '')

			# only show icons for stock IDs that have default icons
			icon_set = gtk.icon_factory_lookup_default(info.stock_id)
			if icon_set is None:
				info.small_icon = None
			else:
				# See what sizes this stock icon really exists at
				sizes = icon_set.get_sizes()
				n_sizes = len(sizes)

				# Use menu size if it exists, otherwise first size found
				size = sizes[0];
				i = 0;
				while(i < n_sizes):
					if(sizes[i] == gtk.ICON_SIZE_MENU):
						size = gtk.ICON_SIZE_MENU
						break
					i += 1

				info.small_icon = self.render_icon(info.stock_id, size)

				if(size != gtk.ICON_SIZE_MENU):
					# Make the result the proper size for our thumbnail
					w, h = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)

					scaled = info.small_icon.scale_simple(w, h, 'bilinear')
					info.small_icon = scaled

			if info.stock_item[3] == 0:
				info.accel_str = ""
			else:
				info.accel_str = \
					gtk.accelerator_name(info.stock_item[3], info.stock_item[2])

			iter = store.append()
			store.set(iter, 0, info, 1, info.stock_id)

		return store

	def on_selection_changed(self, selection):
		treeview = selection.get_tree_view()
		display = treeview.get_data("stock-display")

		model, iter = selection.get_selected()
		if iter:
			info = model.get_value(iter, 0)

			if(info.small_icon and info.stock_item[1]):
				display.type_label.set_text("Icon and Item")

			elif(info.small_icon):
				display.type_label.set_text("Icon Only")

			elif(info.stock_item[1]):
				display.type_label.set_text("Item Only")

			else:
				display.type_label.set_text("???????")

			display.macro_label.set_text(info.macro)
			display.id_label.set_text(info.stock_id)

			if(info.stock_item[1]):
				s = "%s %s" % (info.stock_item[1], info.accel_str)
				display.label_accel_label.set_text_with_mnemonic(s)

			else:
				display.label_accel_label.set_text("")

			if(info.small_icon):
				display.icon_image.set_from_stock(info.stock_id,
									  get_largest_size(info.stock_id))
			else:
				display.icon_image.set_from_pixbuf(None)

		else:
			display.type_label.set_text("No selected item")
			display.macro_label.set_text("")
			display.id_label.set_text("")
			display.label_accel_label.set_text("")
			display.icon_image.set_from_pixbuf(None)

def main():
	StockItemAndIconBrowserDemo()
	gtk.main()

if __name__ == '__main__':
	main()
