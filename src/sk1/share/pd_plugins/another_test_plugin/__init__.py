

import os, wx

from wal import Label, CENTER

from sk1.app_plugins import RS_Plugin

PLG_DIR = __path__[0]
IMG_DIR = os.path.join(PLG_DIR, 'images')

PLUGIN_ICON = 'icon'

def get_plugin(app):
	return Test_Plugin(app)

def load_icon(name):
	icon_file = os.path.join(IMG_DIR, name + '.png')
	return wx.Bitmap(icon_file, wx.BITMAP_TYPE_PNG)

class Test_Plugin(RS_Plugin):

	pid = 'AnotherTestPlugin'
	name = 'Another Test Plugin'

	def build_ui(self):
		self.icon = load_icon(PLUGIN_ICON)
		label = Label(self.panel, self.name, True, 2, (255, 0, 0))
		self.panel.add(label, 0, CENTER, 5)

