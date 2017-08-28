#The test should show IntSpin widget 
#on the main window

import wal

SIZE = (300, 200)

class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        self.spin = wal.IntSpin(self, 5, (0,10), 
            onchange=self.on_change, onenter=self.on_enter)
        self.pack(self.spin)

        self.spin2 = wal.IntSpin(self, 5, (0,10))
        self.pack(self.spin2)

    def on_change(self):
        print self.spin.get_value()

    def on_enter(self):
        print self.spin.get_value()

MW().run()