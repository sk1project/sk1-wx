# The test should show main window which is:
#   1)maximized
#   2)centered after demaximizing
#   3)has size 1000x500
#   4)has minimal size 500x500
#   5)has title "Test 02"

import wal

mw = wal.MainWindow()
mw.set_title("Test 02")
mw.set_minsize((500, 500))
mw.set_size((1000, 700))
mw.center()
mw.maximize()
mw.run()
