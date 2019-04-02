# The test should show Combolist
# widget on the main window

import wal

SIZE = (300, 200)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        items = ['One', 'Two', 'Three']
        self.clist = wal.Combolist(self, items=items, onchange=self.on_change)
        self.clist.set_active(0)
        self.pack(self.clist)

    def on_change(self):
        print self.clist.get_active()
        print self.clist.get_active_value()


MW().run()
