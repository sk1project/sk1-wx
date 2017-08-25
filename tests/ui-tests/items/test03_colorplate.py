import wal

class MW(wal.MainWindow):

	def __init__(self):
		wal.MainWindow.__init__(self)
		self.set_size((300, 200))

		size = (200, 25)
		clrs = [wal.BLACK, wal.GRAY, wal.WHITE, wal.RED, wal.GREEN, wal.BLUE]
		for clr in clrs:
			panel = wal.VPanel(self)
			panel.set_bg(clr)
			panel.pack(size)
			self.pack(panel)

MW().run()
