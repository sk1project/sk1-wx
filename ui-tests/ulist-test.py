import wal

TEST_ULIST = [
		[0, 1, 1, 1, 'Layer3a'],
		[0, 1, 1, 1, 'Layer3b'],
		[1, 1, 1, 1, 'Layer3c'],
		[0, 1, 1, 1, 'Layer3d'],
		[0, 1, 1, 1, 'Layer3f'],
]

class WidgetPanel(wal.HPanel):
	def __init__(self, parent):
		wal.HPanel.__init__(self, parent)

app = wal.Application('wxWidgets')
mw = wal.MainWindow('UList widget', (210, 300))
panel = WidgetPanel(mw)
mw.pack(panel, expand=True, fill=True, padding=10)
app.mw = mw
app.run()
