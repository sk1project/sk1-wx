

import os, wx
from sk1.app_plugins import RS_Plugin
from sk1.widgets import Label, CENTER

PLG_DIR = __path__[0]
IMG_DIR = os.path.join(PLG_DIR, 'images')

def get_plugin(app):
	return Test_Plugin(app)

class Test_Plugin(RS_Plugin):

	pid = 'AnotherTestPlugin'
	name = 'Another Test Plugin'

	def build_ui(self):
		icon_file = os.path.join(IMG_DIR, 'icon.png')
		self.icon = wx.Bitmap(icon_file, wx.BITMAP_TYPE_PNG)
		label = Label(self.panel, self.name, True, 2, (255, 0, 0))
		self.panel.add(label, 0, CENTER, 5)

