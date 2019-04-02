# Needs to be implemented!

import wal

SIZE = (300, 200)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        self.pack(wal.Label(self, 'Needs to be implemented'))


MW().run()
