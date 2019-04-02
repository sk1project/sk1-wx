# The test should show Slider widget
# on the main window

import wal

SIZE = (300, 200)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        self.slider = wal.Slider(self, onchange=self.on_change,
                                 on_final_change=self.on_final_change)
        self.pack(self.slider)

        self.slider2 = wal.Slider(self, vertical=True)
        self.pack(self.slider2)

    def on_change(self):
        print self.slider.get_value()

    def on_final_change(self):
        print 'final', self.slider.get_value()


MW().run()
