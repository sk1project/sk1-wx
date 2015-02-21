
from wal import Label, CENTER

from sk1.app_plugins import RS_Plugin

def get_plugin(app):
	return Test_Plugin(app)

class Test_Plugin(RS_Plugin):

	pid = 'TestPlugin'
	name = 'Test Plugin'

	def build_ui(self):
		label = Label(self.panel, self.name, True, 2, (255, 0, 0))
		self.panel.add(label, 0, CENTER, 5)

