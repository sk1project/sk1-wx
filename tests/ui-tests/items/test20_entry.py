# The test should show different states
# of Entry widget on the main window

import wal

SIZE = (300, 200)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        self.pack(wal.Label(self, 'Regular entry'))

        self.entry1 = wal.Entry(self, 'entry', onchange=self.on_change,
                                onenter=self.on_enter)
        self.pack(self.entry1)

        self.pack(wal.Label(self, 'Readonly entry'))

        self.entry2 = wal.Entry(self, 'r\o entry', editable=False)
        self.pack(self.entry2)

        self.pack(wal.Label(self, 'Multiline entry'))

        self.entry3 = wal.Entry(self, 'Multiline \nentry', multiline=True)
        self.pack(self.entry3, fill=True, expand=True)

    def on_change(self):
        print self.entry1.get_value()

    def on_enter(self):
        print 'enter', self.entry1.get_value()


MW().run()
