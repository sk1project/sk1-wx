import os
import platform

RESTRICTED = ('UniConvertor', 'Python', 'ImageMagick')


def get_path_var():
    path = '' + os.environ["PATH"]
    paths = path.split(os.pathsep)
    ret = []
    for path in paths:
        allow = True
        for item in RESTRICTED:
            if item in path: allow = False
        if allow: ret.append(path)
    return os.pathsep.join(ret)


if os.name == 'nt':

    cur_path = os.path.abspath('..\\..\\..\\sk1-wx-msw')

    devresdir = 'win32-devres'
    if platform.architecture()[0] == '64bit': devresdir = 'win64-devres'

    devres = os.path.join(cur_path, devresdir)
    bindir = os.path.join(devres, 'dlls') + os.pathsep
    magickdir = os.path.join(devres, 'dlls', 'modules') + os.pathsep

    os.environ["PATH"] = magickdir + bindir + get_path_var()
    os.environ["MAGICK_CODER_MODULE_PATH"] = magickdir
    os.environ["MAGICK_CODER_FILTER_PATH"] = magickdir
    os.environ["MAGICK_CONFIGURE_PATH"] = magickdir
    os.environ["MAGICK_HOME"] = magickdir

    os.chdir(os.path.join(devres, 'dlls'))

import wal


class ColorPanel(wal.ScrolledPanel):
    def __init__(self, parent):
        wal.ScrolledPanel.__init__(self, parent)
        keys = wal.UI_COLORS.keys()
        grid = wal.GridPanel(self, len(keys), 2, 10, 10)
        for item in keys:
            grid.pack(wal.Label(grid, item))
            panel = wal.VPanel(grid)
            panel.pack((80, 50))
            panel.set_bg(wal.UI_COLORS[item])
            grid.pack(panel)
        self.pack(grid, padding=10)


app = wal.Application('wxWidgets')
mw = wal.MainWindow(app, 'WAL colors', (350, 550))
top_panel = wal.VPanel(mw)
mw.pack(top_panel, expand=True, fill=True)
panel = ColorPanel(top_panel)
top_panel.pack(panel, expand=True, fill=True)
app.mw = mw
app.run()
