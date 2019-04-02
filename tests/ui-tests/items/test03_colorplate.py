# The test should generate six colored
# rectangles on the main window

import wal

SIZE = (300, 200)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        size = (200, 25)
        clrs = [wal.BLACK, wal.GRAY, wal.WHITE, wal.RED, wal.GREEN, wal.BLUE]
        for clr in clrs:
            panel = wal.VPanel(self)
            panel.set_bg(clr)
            panel.pack(size)
            self.pack(panel)


MW().run()
