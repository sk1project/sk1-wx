# The test should show vertical
# line (PLine) on the main window

import wal

SIZE = (300, 200)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self, vertical=False)
        self.set_size(SIZE)

        self.pack((10, 10))
        self.pack(wal.PLine(self), fill=True)


MW().run()
