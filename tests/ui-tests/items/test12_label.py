# The test should show six different
# labels on the main window

import wal

SIZE = (300, 300)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        self.pack(wal.Label(self, 'Regular label'), padding=10)
        self.pack(wal.Label(self, 'Bold label', fontbold=True), padding=10)
        self.pack(wal.Label(self, 'Large label', fontsize=2), padding=10)
        self.pack(wal.Label(self, 'Small label', fontsize=-1), padding=10)
        self.pack(wal.Label(self, 'Colored label', fg=wal.RED), padding=10)
        label = wal.Label(self, 'Disabled label')
        label.set_enable(False)
        self.pack(label, padding=10)


MW().run()
