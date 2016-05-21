import wal

class ColorPanel(wal.ScrolledPanel):
	def __init__(self, parent):
		wal.ScrolledPanel.__init__(self, parent)
		keys = wal.UI_COLORS.keys()
		grid = wal.GridPanel(self, len(keys), 2, 10, 10)
		for item in keys:
			grid.pack(wal.Label(grid, item))
			panel = wal.VPanel(grid)
			panel.pack((80, 50))
			panel.set_bg(wal.UI_COLORS[item])
			grid.pack(panel)
		self.pack(grid, padding=10)


app = wal.Application('wxWidgets')
mw = wal.MainWindow('WAL colors', (350, 550))
top_panel = wal.VPanel(mw)
mw.pack(top_panel, expand=True, fill=True)
panel = ColorPanel(top_panel)
top_panel.pack(panel, expand=True, fill=True)
app.mw = mw
app.run()
