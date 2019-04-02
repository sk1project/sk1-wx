# The test should show SpinButton widget
# on the main window

import wal

SIZE = (300, 200)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        self.spin = wal.SpinButton(self, 5, (0, 20), onchange=self.on_change)
        self.pack(self.spin)

        self.spin2 = wal.SpinButton(self, 5, (0, 20), vertical=False)
        self.pack(self.spin2)

    def on_change(self, event):
        print self.spin.get_value()


MW().run()
