
import cups

import wal

def get_printers():
	conn = cups.Connection()
	printers = conn.getPrinters()
	default = conn.getDefault()
	return printers, default

def get_printer_attrs(name):
	conn = cups.Connection()
	return conn.getPrinterAttributes(name)

def attr_to_str(attr):
	if isinstance(attr, list) or  isinstance(attr, tuple):
		ret = ''
		for item in attr:
			ret += str(item) + '\n'
	else:
		ret = str(attr)
	return ret


class TestPanel(wal.VPanel):

	value = None
	dvalue = None
	prn_list = []
	printer = None
	details = []
	printer_attrs = None
	attrs = []

	def __init__(self, parent):
		wal.VPanel.__init__(self, parent)

		#--- Printer list
		self.prn_dict, default = get_printers()
		self.prn_list = self.prn_dict.keys()
		self.prn_list.sort()

		hpanel = wal.HPanel(self)
		hpanel.pack((10, 1))
		hpanel.pack(wal.Label(hpanel, 'Device name:'))

		self.prn_combo = wal.Combolist(hpanel, items=self.prn_list,
									onchange=self.printer_changed)
		hpanel.pack(self.prn_combo, padding=10)
		if self.prn_list:
			self.prn_combo.set_active(self.prn_list.index(default))

		self.pack(hpanel, fill=True, padding=10)

		#--- Printer details
		self.pack(wal.Label(hpanel, 'Printer details', fontbold=True, fontsize=2))
		hpanel = wal.HPanel(self)

		if self.prn_list:
			self.printer = self.prn_dict[self.prn_combo.get_active_value()]
			self.details = self.printer.keys()
			self.details.sort()
		self.details_list = wal.SimpleList(hpanel, self.details,
								on_select=self.details_changed,
								on_activate=self.details_changed)
		hpanel.pack(self.details_list, expand=True, fill=True, padding=10)

		val = ''
		if self.details:
			self.details_list.set_active(0)
			val = attr_to_str(self.printer[self.details[0]])

		self.dvalue = wal.Entry(hpanel, val, multiline=True, editable=False)
		hpanel.pack(self.dvalue, expand=True, fill=True, padding=10)

		self.pack(hpanel, expand=True, fill=True, padding=10)

		self.pack(wal.Label(self, '%d records' % len(self.details)))
		self.pack((10, 10))

		#--- Printer attributes
		self.pack(wal.Label(hpanel, 'Printer attributes', fontbold=True, fontsize=2))
		hpanel = wal.HPanel(self)

		if self.prn_list:
			self.printer_attrs = get_printer_attrs(self.prn_combo.get_active_value())
			self.attrs = self.printer_attrs.keys()
			self.attrs.sort()
		self.attrs_list = wal.SimpleList(hpanel, self.attrs,
								on_select=self.attrs_changed,
								on_activate=self.attrs_changed)
		hpanel.pack(self.attrs_list, expand=True, fill=True, padding=10)

		val = ''
		if self.attrs:
			self.attrs_list.set_active(0)
			val = attr_to_str(self.printer_attrs[self.attrs[0]])

		self.value = wal.Entry(hpanel, val, multiline=True, editable=False)
		hpanel.pack(self.value, expand=True, fill=True, padding=10)

		self.pack(hpanel, expand=True, fill=True, padding=10)

		self.pack(wal.Label(self, '%d records' % len(self.attrs)))

	def details_changed(self, item):
		if not self.printer or not self.dvalue: return
		self.dvalue.set_value(attr_to_str(self.printer[item]))

	def attrs_changed(self, item):
		if not self.printer or not self.value: return
		self.value.set_value(attr_to_str(self.printer_attrs[item]))

	def printer_changed(self, *args):
		self.printer = self.prn_dict[self.prn_combo.get_active_value()]

		self.details = self.printer.keys()
		self.details.sort()
		self.details_list.update(self.details)
		self.details_list.set_active(0)

		self.printer_attrs = get_printer_attrs(self.prn_combo.get_active_value())
		self.attrs = self.printer_attrs.keys()
		self.attrs.sort()
		self.attrs_list.update(self.attrs)
		self.attrs_list.set_active(0)


app = wal.Application('wxWidgets')
mw = wal.MainWindow('CUPS printers', (750, 800))
top_panel = TestPanel(mw)
mw.pack(top_panel, expand=True, fill=True)
app.mw = mw
app.run()
