# The test should show two types of
# HtmlLabel on the main window

import wal

SIZE = (300, 200)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        self.pack(wal.HtmlLabel(self, 'https://sk1project.net'), padding=10)
        self.pack(wal.HtmlLabel(self, 'Project site',
                                'https://sk1project.net'), padding=10)


MW().run()
