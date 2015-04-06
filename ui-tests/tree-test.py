import wx
import wal


class WidgetPanel(wal.VPanel):
	def __init__(self, parent):
		wal.VPanel.__init__(self, parent)

		exp = wal.ExpandedPanel(self, 'Test options')
		self.pack(exp, fill=True)
		exp.pack(wal.Button(exp, 'Test button'))

		data = []
		root = wal.TreeElement('root')
		prov = wx.ArtProvider_GetBitmap
		icon = prov(wx.ART_CDROM, wx.ART_OTHER, wal.SIZE_16)
		root.icon = icon
		for item in range(5):
			el = wal.TreeElement('Element %d' % item)
			root.childs.append(el)
		data.append(root)
		data.append(root)

		self.tree = wal.TreeWidget(self, data, on_select=self.selected)
		self.pack(self.tree, expand=True, fill=True, padding=2)
		self.tree.expand_all()

	def selected(self, item):
		print item

app = wal.Application('wxWidgets')
mw = wal.MainWindow('Tree widget', (350, 550))
panel = WidgetPanel(mw)
mw.pack(panel, expand=True, fill=True, padding=10)
app.mw = mw
app.run()
