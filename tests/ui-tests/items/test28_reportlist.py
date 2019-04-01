# The test should show ReportList widget
# on the main window

import wal

SIZE = (300, 200)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)
        items = [['Name', 'Value'],
                 ['One', '1'],
                 ['Two', '2'],
                 ['Three', '3'], ]

        lst1 = wal.ReportList(self, items, False)

        self.pack(lst1, padding=5, fill=True)


MW().run()
