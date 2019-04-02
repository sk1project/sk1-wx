# The test should show horizontal
# line (HLine) on the main window

import wal

SIZE = (300, 200)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self, vertical=False)
        self.set_size(SIZE)

        self.pack(wal.HLine(self), expand=True, fill=True)


MW().run()
