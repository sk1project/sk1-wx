# The test should show three grouped radiobuttons
# on the main window

import wal

SIZE = (300, 200)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        self.radio1 = wal.Radiobutton(self, 'Radiobutton 1',
                                      onclick=self.on_click, group=True)
        self.pack(self.radio1)

        self.radio2 = wal.Radiobutton(self, 'Radiobutton 2')
        self.pack(self.radio2)

        self.radio3 = wal.Radiobutton(self, 'Radiobutton 3',
                                      onclick=self.on_click3)
        self.pack(self.radio3)

    def on_click(self):
        print '-' * 30
        print self.radio1.get_value()
        print self.radio2.get_value()
        print self.radio3.get_value()

    def on_click3(self):
        print '-' * 30
        print self.radio1.get_value()
        print self.radio2.get_value()
        print self.radio3.get_value()


MW().run()
