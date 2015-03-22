import wal

TESTLIST = ['Value1', 'Value2', 'Value3', 'Value4', 'Value5', 'Value6']

TESTMULTILIST = [
		['Name1', 'Name2', 'Name3'],
		['Value1', 'Value2', 'Value3'],
		['Value1', 'Value2', 'Value3'],
		['Value1', 'Value2', 'Value3'],
		['Value1', 'Value2', 'Value3'],
		['Value1', 'Value2', 'Value3'],
]
class WidgetPanel(wal.HPanel):
	def __init__(self, parent):
		wal.HPanel.__init__(self, parent)

		self.slist = wal.SimpleList(self, TESTLIST, on_select=self.selected,
								on_activate=self.activated)
		self.pack(self.slist, expand=True, fill=True, padding=10)

		self.report = wal.ReportList(self, TESTMULTILIST,
									on_select=self.selected,
									on_activate=self.activated)
		self.pack(self.report, expand=True, fill=True, padding=10)

	def selected(self, item):
		print item

	def activated(self, item):
		print item

app = wal.Application('wxWidgets')
mw = wal.MainWindow('List widget', (750, 550))
panel = WidgetPanel(mw)
mw.pack(panel, expand=True, fill=True, padding=10)
app.mw = mw
app.run()
