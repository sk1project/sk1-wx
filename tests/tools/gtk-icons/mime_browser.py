#!/usr/bin/env python
# based on http://www.daa.com.au/pipermail/pygtk/2003-August/005644.html

import pygtk

pygtk.require('2.0')
import gtk
import gobject


class MimeList(gtk.TreeView):
    def __init__(self):
        gtk.TreeView.__init__(self)
        self.init_model()
        self.init_view_columns()

    def init_model(self):
        store = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
        icon_theme = gtk.icon_theme_get_default()
        names = list(icon_theme.list_icons())
        names.sort()
        print 'Icon theme listed'
        print 'Generating icon previews...  0%'
        sz = float(len(names))
        indx = 0
        pindex = 0
        for name in names:
            try:
                store.append((icon_theme.load_icon(name, 32, 0), name))
            except:
                pass

            indx += 1.0
            point = (indx / sz) * 100.0 // 5
            if pindex < point:
                pindex = point
                print 'Generating icon previews...%3d%%' % (pindex * 5)

        self.set_model(store)

    def get_icon_pixbuf(self, stock):
        return self.render_icon(stock_id=getattr(gtk, stock),
                                size=gtk.ICON_SIZE_MENU,
                                detail=None)

    def init_view_columns(self):
        col = gtk.TreeViewColumn()
        col.set_max_width(48)
        col.set_title('Icons')
        render_pixbuf = gtk.CellRendererPixbuf()
        col.pack_start(render_pixbuf, expand=False)
        col.add_attribute(render_pixbuf, 'pixbuf', 0)
        self.append_column(col)

        col = gtk.TreeViewColumn()
        col.set_title('Stock Names')
        render_text = gtk.CellRendererText()
        col.pack_start(render_text, expand=False)
        col.add_attribute(render_text, 'text', 1)
        self.append_column(col)
        self.set_rules_hint(True)


if __name__ == '__main__':
    w = gtk.Window()
    w.set_title('Stock Items')
    w.set_size_request(width=400, height=700)
    w.connect('destroy', gtk.mainquit)
    sw = gtk.ScrolledWindow()
    sw.add(MimeList())
    w.add(sw)
    w.show_all()
    gtk.mainloop()
