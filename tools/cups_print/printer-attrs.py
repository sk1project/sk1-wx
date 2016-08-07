
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

def get_printer_options(name):
	conn = cups.Connection()
	dests = conn.getDests()
	for item in dests.keys():
		if item[0] == name:
			return dests[item].options
	return {}

def attr_to_str(attr):
	if isinstance(attr, list) or  isinstance(attr, tuple):
		ret = ''
		for item in attr:
			ret += str(item) + '\n'
	else:
		ret = str(attr)
	return ret


class DetailsPanel(wal.VPanel):

	prn_details = {}
	details = []
	details_list = None
	value = None

	def __init__(self, parent, details):
		wal.VPanel.__init__(self, parent)
		hpanel = wal.HPanel(self)

		self.details_list = wal.SimpleList(hpanel, [],
								on_select=self.details_changed,
								on_activate=self.details_changed)
		hpanel.pack(self.details_list, expand=True, fill=True)

		hpanel.pack((10, 10))

		self.value = wal.Entry(hpanel, '', multiline=True, editable=False)
		hpanel.pack(self.value, expand=True, fill=True)

		self.pack(hpanel, fill=True, expand=True, padding_all=10)

		self.status_label = wal.Label(self, '---')
		self.pack(self.status_label, fill=True, align_center=False, padding_all=10)

		self.set_prn_details(details)

	def set_prn_details(self, details):
		cur_val = ''
		if self.details:
			cur_val = self.details[self.details_list.get_active()]
		self.prn_details = details
		self.details = self.prn_details.keys()
		self.details.sort()
		self.details_list.update(self.details)
		index = 0
		if cur_val in self.details:
			index = self.details.index(cur_val)
		self.details_list.set_active(index)

	def details_changed(self, item):
		if not self.prn_details or not self.value: return
		self.value.set_value(attr_to_str(self.prn_details[item]))
		self.status_label.set_text('%d records' % len(self.prn_details))

class AttrsPanel(wal.VPanel):

	prn_attrs = {}
	attrs = []
	attrs_list = None
	value = None

	def __init__(self, parent, attrs):
		wal.VPanel.__init__(self, parent)
		hpanel = wal.HPanel(self)

		self.attrs_list = wal.SimpleList(hpanel, [],
								on_select=self.attrs_changed,
								on_activate=self.attrs_changed)
		hpanel.pack(self.attrs_list, expand=True, fill=True)

		hpanel.pack((10, 10))

		self.value = wal.Entry(hpanel, '', multiline=True, editable=False)
		hpanel.pack(self.value, expand=True, fill=True)

		self.pack(hpanel, fill=True, expand=True, padding_all=10)

		self.status_label = wal.Label(self, '---')
		self.pack(self.status_label, fill=True, align_center=False, padding_all=10)

		self.set_prn_attrs(attrs)

	def set_prn_attrs(self, attrs):
		cur_val = ''
		if self.attrs:
			cur_val = self.attrs[self.attrs_list.get_active()]
		self.prn_attrs = attrs
		self.attrs = self.prn_attrs.keys()
		self.attrs.sort()
		self.attrs_list.update(self.attrs)
		index = 0
		if cur_val in self.attrs:
			index = self.attrs.index(cur_val)
		self.attrs_list.set_active(index)

	def attrs_changed(self, item):
		if not self.prn_attrs or not self.value: return
		self.value.set_value(attr_to_str(self.prn_attrs[item]))
		self.status_label.set_text('%d records' % len(self.prn_attrs))

class OptionPanel(wal.VPanel):

	prn_options = {}
	options = []
	options_list = None
	value = None

	def __init__(self, parent, options):
		wal.VPanel.__init__(self, parent)
		hpanel = wal.HPanel(self)

		self.options_list = wal.SimpleList(hpanel, [],
								on_select=self.options_changed,
								on_activate=self.options_changed)
		hpanel.pack(self.options_list, expand=True, fill=True)

		hpanel.pack((10, 10))

		self.value = wal.Entry(hpanel, '', multiline=True, editable=False)
		hpanel.pack(self.value, expand=True, fill=True)

		self.pack(hpanel, fill=True, expand=True, padding_all=10)

		self.status_label = wal.Label(self, '---')
		self.pack(self.status_label, fill=True, align_center=False, padding_all=10)

		self.set_prn_options(options)

	def set_prn_options(self, options):
		cur_val = ''
		if self.options:
			cur_val = self.options[self.options_list.get_active()]
		self.prn_options = options
		self.options = self.prn_options.keys()
		self.options.sort()
		self.options_list.update(self.options)
		index = 0
		if cur_val in self.options:
			index = self.options.index(cur_val)
		self.options_list.set_active(index)

	def options_changed(self, item):
		if not self.prn_options or not self.value: return
		self.value.set_value(attr_to_str(self.prn_options[item]))
		self.status_label.set_text('%d records' % len(self.prn_options))

class TestPanel(wal.VPanel):

	prn_dict = {}
	prn_list = []
	details_panel = None
	attrs_panel = None

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

		self.pack(hpanel, padding=10)

		#--- Printer tabs

		self.nb = wal.Notebook(self)

		details = self.prn_dict[default]
		self.details_panel = DetailsPanel(self.nb, details)
		self.nb.add_page(self.details_panel, 'Device details')

		attrs = get_printer_attrs(default)
		self.attrs_panel = AttrsPanel(self.nb, attrs)
		self.nb.add_page(self.attrs_panel, 'Device attributes')

		options = get_printer_options(default)
		self.options_panel = OptionPanel(self.nb, options)
		self.nb.add_page(self.options_panel, 'Device options')

		self.pack(self.nb, fill=True, expand=True, padding_all=10)

	def printer_changed(self, *args):
		if not self.attrs_panel:return
		details = self.prn_dict[self.prn_combo.get_active_value()]
		self.details_panel.set_prn_details(details)

		attrs = get_printer_attrs(self.prn_combo.get_active_value())
		self.attrs_panel.set_prn_attrs(attrs)

		options = get_printer_options(self.prn_combo.get_active_value())
		self.options_panel.set_prn_options(options)


app = wal.Application('wxWidgets')
mw = wal.MainWindow('CUPS printers', (750, 450))
top_panel = TestPanel(mw)
mw.pack(top_panel, expand=True, fill=True)
app.mw = mw
app.run()
