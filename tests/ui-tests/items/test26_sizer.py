# The test should show Slider widget
# on the main window

import wal

SIZE = (500, 200)


class MW(wal.MainWindow):

    def __init__(self):
        wal.MainWindow.__init__(self)
        self.set_size(SIZE)

        hpanel = wal.HPanel(self)
        self.pack(hpanel, fill=True, expand=True)

        lpanel = wal.VPanel(hpanel)
        client = wal.VPanel(lpanel)
        client.pack((200, 0))
        lpanel.pack(client)
        lpanel.set_bg(wal.RED)
        hpanel.pack(lpanel, fill=True)

        hsizer = wal.HSizer(hpanel)
        hsizer.set_client(hpanel, client, 100)
        hpanel.pack(hsizer, fill=True)

        rpanel = wal.VPanel(hpanel)
        rpanel.pack((20, 20))
        rpanel.set_bg(wal.BLUE)
        hpanel.pack(rpanel, fill=True, expand=True)


MW().run()
