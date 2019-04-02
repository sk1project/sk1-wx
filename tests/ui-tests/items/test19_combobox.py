# The test should show Combobox and
# FloatCombobox widgets on the main window

import wal

SIZE = (300, 200)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        items = ['One', 'Two', 'Three']

        self.pack(wal.Label(self, 'Combobox:'))
        self.cmb = wal.Combobox(self, items=items, onchange=self.on_change)
        self.pack(self.cmb)

        self.pack((10, 10))

        self.pack(wal.Label(self, 'FloatCombobox:'))
        self.fcmb = wal.FloatCombobox(self, items=range(10),
                                      onchange=self.on_change2)
        self.pack(self.fcmb)

    def on_change(self):
        print self.cmb.get_value()

    def on_change2(self):
        print self.fcmb.get_value()


MW().run()
