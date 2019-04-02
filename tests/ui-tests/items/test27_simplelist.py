# The test should show SimpleList widget
# on the main window

import wal

SIZE = (200, 400)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)
        items = ['One', 'Two', 'Three', 'One', 'Two', 'Three']

        lst1 = wal.SimpleList(self, items, False)

        self.pack(lst1, padding=5, fill=True)

        lst2 = wal.SimpleList(self, items, False, alt_color=True)

        self.pack(lst2, padding=5, fill=True)


MW().run()
