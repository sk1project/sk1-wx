import wal


class WidgetPanel(wal.HPanel):
	def __init__(self, parent):
		wal.HPanel.__init__(self, parent)

		panel = wal.LabeledPanel(self, text='LabeledPanel')
		self.pack(panel, fill=True, expand=True, padding_all=10)

		panel.pack(wal.Label(panel, 'Internal widget'))


app = wal.Application('wxWidgets')
mw = wal.MainWindow('LabeledPanel widget', (250, 350))
panel = WidgetPanel(mw)
mw.pack(panel, expand=True, fill=True, padding=10)
app.mw = mw
app.run()
