import wal


class WidgetPanel(wal.HPanel):
	def __init__(self, parent):
		wal.HPanel.__init__(self, parent)

		self.win = wal.ScrolledPanel(self, border=True)
#		self.win.set_virtual_size((160, 1600))
		self.win.set_bg(wal.WHITE)

		self.pack(self.win, expand=True, fill=True, padding_all=10)

	def selected(self, item):
		print item

	def activated(self, item):
		print item

app = wal.Application('wxWidgets')
mw = wal.MainWindow('ScrolledPanel widget', (250, 350))
panel = WidgetPanel(mw)
mw.pack(panel, expand=True, fill=True, padding=10)
app.mw = mw
app.run()
