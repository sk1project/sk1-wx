import wal

TEST_LIST = [
		[0, 1, 1, 1, 1, 'Layer3a'],
		[0, 1, 1, 1, 1, 'Layer3b'],
		[1, 1, 0, 1, 1, 'Layer3c'],
		[0, 1, 1, 0, 1, 'Layer3d'],
		[0, 1, 1, 1, 1, 'Layer3f'],
]

BITMAPS = [
		'gtk-justify-fill', 'gtk-yes',
		'gtk-stop', 'gtk-index',
		'gtk-stop', 'gtk-edit',
		'gtk-print-error', 'gtk-print',
		'gtk-stop', 'gtk-edit',
]

class WidgetPanel(wal.HPanel):
	def __init__(self, parent):
		wal.HPanel.__init__(self, parent)
		pnl = wal.VPanel(self, border=True)
		self.lst = wal.LayerList(pnl, TEST_LIST, BITMAPS, on_change=self.changes)
		pnl.pack(self.lst, fill=True, expand=True)
		self.pack(pnl, padding_all=10, fill=True, expand=True)

	def changes(self, item, column):
		if column < 4:
			if not column:
				for line in TEST_LIST: line[0] = 0
				TEST_LIST[item][0] = 1
			else:
				TEST_LIST[item][column] = abs(TEST_LIST[item][column] - 1)
			self.lst.update(TEST_LIST)



app = wal.Application('wxWidgets')
mw = wal.MainWindow('LayerList widget', (210, 300))
panel = WidgetPanel(mw)
mw.pack(panel, expand=True, fill=True, padding=10)
app.mw = mw
app.run()
