#The test should show Spin widget 
#on the main window

import wal

SIZE = (300, 200)

class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        self.spin = wal.Spin(self, 5, (0,20), onchange=self.on_change)
        self.pack(self.spin)

    def on_change(self):
        print self.spin.get_value()
        
MW().run()