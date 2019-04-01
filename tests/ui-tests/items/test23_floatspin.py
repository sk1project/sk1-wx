# The test should show FloatSpin widget
# on the main window

import wal

SIZE = (300, 200)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        self.spin = wal.FloatSpin(self, 5, (0, 30), width=4,
                                  onchange=self.on_change,
                                  onenter=self.on_enter)
        self.pack(self.spin)

        self.spin2 = wal.FloatSpin(self, 5, (0, 100), digits=4)
        self.pack(self.spin2)

    def on_change(self):
        print self.spin.get_value()

    def on_enter(self):
        print self.spin.get_value()


MW().run()
