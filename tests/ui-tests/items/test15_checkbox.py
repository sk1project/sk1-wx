# The test should show three different
# types of Checkbox on the main window

import wal

SIZE = (300, 200)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        self.check1 = wal.Checkbox(self, 'Regular checkbox',
                                   onclick=self.on_click)
        self.pack(self.check1)

        self.check2 = wal.Checkbox(self, 'Right checkbox',
                                   right=True)
        self.pack(self.check2)

        self.check3 = wal.NumCheckbox(self, 'Numeric checkbox',
                                      onclick=self.on_click3)
        self.pack(self.check3)

    def on_click(self):
        print self.check1.get_value()

    def on_click3(self):
        print self.check3.get_value()


MW().run()
