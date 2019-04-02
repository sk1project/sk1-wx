# The test should show differen
# button states on the main window

import wal

SIZE = (300, 300)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        self.pack(wal.Button(self, 'Just a button'), padding=10)
        self.pack(wal.Button(self, 'Default button', default=True), padding=10)
        self.pack(wal.Button(self, 'Button with callback',
                             onclick=self.on_click), padding=10)
        self.pack(wal.Button(self, 'Button with tooltip',
                             tooltip='Button tooltip'), padding=10)
        btn = wal.Button(self, 'Disabled button')
        btn.set_enable(False)
        self.pack(btn, padding=10)

    def on_click(self):
        print 'Works!'


MW().run()
