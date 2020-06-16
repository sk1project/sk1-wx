# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Ihor E. Novikov
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.


import cairo
import os
from cStringIO import StringIO

import wal
from sk1 import _, events, dialogs
from sk1.app_plugins import RsPlugin
from sk1.pwidgets import CBMiniPalette
from sk1.resources import get_icon
from uc2 import cms, libgeom, uc2const
from uc2.formats.sk2 import crenderer
from uc2.utils import fsutils
from uc2.utils.config import XmlConfigParser

PLG_DIR = __path__[0]
IMG_DIR = os.path.join(PLG_DIR, 'images')


def make_artid(name):
    return os.path.join(IMG_DIR, name + '.png')


def get_plugin(app):
    return IconizerPlugin(app)


PLUGIN_ICON = make_artid('icon')

COLORS = [
    ('#FFFFFF', 'White'),
    ('#D4D0C8', 'Win2k'),
    ('#ECE9D8', 'WinXP'),
    ('#E0DFE3', 'WinXP Silver'),
    ('#F0F0F0', 'Win7'),
    ('#F2F1F0', 'Ubuntu'),
]

SIZE = 190
REFRESH_DELAY = 100


class IconizerConfig(XmlConfigParser):
    system_encoding = 'utf-8'
    bg_color = (1.0, 1.0, 1.0)
    draw_selected = False
    draw_border = False
    save_dir = '~'


class ImageCanvas(wal.ScrolledCanvas, wal.DrawableWidget):
    bitmap = None
    show_border = False

    def __init__(self, parent, bgcolor=None):
        wal.ScrolledCanvas.__init__(self, parent)
        wal.DrawableWidget.__init__(self)
        bgcolor = bgcolor or wal.WHITE
        self.set_bg(bgcolor)

        sb = wal.ScrollBar(self)
        self.sb_width = sb.get_size()[0]
        sb.destroy()

    def paint(self):
        if self.bitmap is None:
            w = h = 0
        else:
            w, h = wal.get_bitmap_size(self.bitmap)
        self.set_virtual_size((max(SIZE - self.sb_width - 2, w),
                               max(SIZE - self.sb_width - 2, h)))
        self.prepare_dc(self.pdc)
        if self.bitmap is None:
            self.set_gc_stroke(wal.UI_COLORS['border'][:3])
            self.gc_draw_line(0, 0, SIZE, SIZE)
            self.gc_draw_line(SIZE, 0, 0, SIZE)
        else:
            x = (SIZE - w) / 2 if SIZE > w else 0
            y = (SIZE - h) / 2 if SIZE > h else 0
            self.draw_bitmap(self.bitmap, x, y)
            if self.show_border:
                self.set_stroke(wal.UI_COLORS['border'][:3], 1.0,
                                [2, 2])
                shift = 10
                items = [(x - shift, y - 1, x + w + shift, y - 1),
                         (x - shift, y + h, x + w + shift, y + h),
                         (x - 1, y - shift, x - 1, y + h + shift),
                         (x + w, y - shift, x + w, y + h + shift), ]
                for item in items:
                    self.draw_line(*item)


class Spacer(wal.VPanel):
    def __init__(self, parent):
        wal.VPanel.__init__(self, parent)
        self.pack((SIZE, 1))
        self.set_bg(wal.UI_COLORS['border'][:3])


class ImageViewer(wal.HPanel):
    def __init__(self, parent, bg):
        wal.HPanel.__init__(self, parent)
        self.set_bg(wal.UI_COLORS['border'][:3])
        self.pack((1, SIZE))
        panel = wal.VPanel(self)
        panel.set_bg(wal.UI_COLORS['bg'][:3])
        panel.pack(Spacer(panel))
        self.canvas = ImageCanvas(panel, cms.val_255(bg))
        panel.pack(self.canvas, fill=True, expand=True)
        info_panel = wal.VPanel(panel)
        info_panel.set_bg(wal.UI_COLORS['entry_bg'])
        self.info = wal.Label(info_panel, '---')
        info_panel.pack(self.info, padding_all=2)
        panel.pack(Spacer(panel))
        panel.pack(info_panel, fill=True)
        panel.pack(Spacer(panel))
        self.pack(panel, fill=True)
        self.pack((1, SIZE + info_panel.get_size()[1] + 3))

    def set_canvas_bg(self, color):
        self.canvas.set_bg(cms.val_255(color))
        self.canvas.refresh()

    def set_picture(self, picture):
        if picture is not None:
            picture = wal.stream_to_bitmap(picture)
            w, h = wal.get_bitmap_size(picture)
            self.info.set_text(_('Size:') + ' %d x %d px' % (w, h))
        else:
            self.info.set_text('---')
        self.canvas.bitmap = picture
        self.canvas.refresh()
        self.layout()

    def set_border(self, val):
        self.canvas.show_border = val
        self.canvas.refresh()


class IconizerPlugin(RsPlugin):
    pid = 'IconizerPlugin'
    name = _('Iconizer')
    active_transform = None
    transforms = {}
    picture = None
    config = None
    bg_color_btn = None
    pallete = None
    viewer = None
    border_check = None
    sel_check = None
    apply_btn = None
    timer = None

    def build_ui(self):
        self.icon = get_icon(PLUGIN_ICON)

        self.config = IconizerConfig()
        config_dir = self.app.appdata.app_config_dir
        config_file = os.path.join(config_dir, 'iconizer_config.xml')
        self.config.load(config_file)

        self.panel.pack((5, 5))
        hpanel = wal.HPanel(self.panel)
        hpanel.pack(wal.Label(hpanel, _('Background:')))
        self.bg_color_btn = wal.ColorButton(hpanel, self.config.bg_color,
                                            onchange=self.update, silent=False)
        hpanel.pack((5, 5))
        hpanel.pack(self.bg_color_btn)
        self.panel.pack(hpanel, padding=5)

        self.pallete = CBMiniPalette(self.panel, COLORS,
                                     onclick=self.bg_color_btn.set_value)
        self.panel.pack(self.pallete)

        self.panel.pack((10, 10))

        self.viewer = ImageViewer(self.panel, self.config.bg_color)
        self.panel.pack(self.viewer)

        self.panel.pack((10, 10))

        check_panel = wal.VPanel(self.panel)

        self.border_check = wal.Checkbox(check_panel, _('Show image border'),
                                         value=self.config.draw_border,
                                         onclick=self.update)
        check_panel.pack(self.border_check, align_center=False)

        self.sel_check = wal.Checkbox(check_panel, _('Draw selected only'),
                                      value=self.config.draw_selected,
                                      onclick=self.update)
        check_panel.pack(self.sel_check, align_center=False)

        self.panel.pack(check_panel)

        self.apply_btn = wal.Button(self.panel, _('Save image'),
                                    onclick=self.apply_action)
        self.panel.pack(self.apply_btn, fill=True, padding_all=5)

        self.panel.pack((5, 5))

        self.panel.pack(wal.HLine(self.panel), fill=True)

        events.connect(events.DOC_CHANGED, self.update)
        events.connect(events.SELECTION_CHANGED, self.update)
        events.connect(events.DOC_MODIFIED, self.update)

        self.timer = wal.CanvasTimer(self.panel,
                                     delay=REFRESH_DELAY,
                                     on_timer=self.repaint)

    def show_signal(self, *args):
        self.update()

    def save_config(self):
        config_dir = self.app.appdata.app_config_dir
        config_file = os.path.join(config_dir, 'iconizer_config.xml')
        self.config.save(config_file)

    def render(self, sel_flag=False):
        doc = self.app.current_doc
        if not doc:
            return
        if sel_flag:
            if not doc.selection.objs:
                return None
            w, h = libgeom.bbox_size(doc.selection.bbox)
            x, y = libgeom.bbox_center(doc.selection.bbox)
            trafo = (1.0, 0, 0, -1.0, w / 2.0 - x, h / 2.0 + y)
        else:
            page = doc.active_page
            w, h = page.page_format[1]
            trafo = (1.0, 0, 0, -1.0, w / 2.0, h / 2.0)

        canvas_matrix = cairo.Matrix(*trafo)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w), int(h))
        ctx = cairo.Context(surface)
        ctx.set_matrix(canvas_matrix)

        rend = crenderer.CairoRenderer(doc.cms)

        if sel_flag:
            objs = doc.selection.objs
            for obj in objs:
                layer = doc.methods.get_parent_layer(obj)
                rend.antialias_flag = layer.properties[3] == 1
                rend.render(ctx, [obj, ])
        else:
            page = doc.active_page
            layers = doc.methods.get_visible_layers(page)
            for item in layers:
                rend.antialias_flag = item.properties[3] == 1
                rend.render(ctx, item.childs)

        image_stream = StringIO()
        surface.write_to_png(image_stream)
        return image_stream

    def update(self, *_args):
        if self.is_shown():
            self.timer.restart()

    def repaint(self, *_args):
        color = self.bg_color_btn.get_value()
        if not color == self.config.bg_color:
            self.config.bg_color = color
            self.save_config()
            self.viewer.set_canvas_bg(self.config.bg_color)
        if not self.sel_check.get_value() == self.config.draw_selected:
            self.config.draw_selected = not self.config.draw_selected
            self.save_config()
        if not self.border_check.get_value() == self.config.draw_border:
            self.config.draw_border = not self.config.draw_border
            self.save_config()
        self.viewer.set_border(self.config.draw_border)
        self.picture = self.render(self.config.draw_selected)
        self.viewer.set_picture(self.picture)
        self.apply_btn.set_enable(self.picture is not None)
        self.timer.stop()

    def apply_action(self):
        if not self.picture:
            return
        doc_file = 'image'
        doc_file = os.path.join(self.config.save_dir, doc_file)
        doc_file = dialogs.get_save_file_name(self.app.mw, doc_file,
                                              _('Save image as...'),
                                              file_types=[uc2const.PNG],
                                              path_only=True)
        if doc_file:
            try:
                fileptr = fsutils.get_fileptr(doc_file, True)
                fileptr.write(self.picture.getvalue())
                fileptr.close()
            except Exception:
                first = _('Cannot save image:')
                msg = "%s\n'%s'." % (first, doc_file) + '\n'
                msg += _('Please check file name and write permissions')
                dialogs.error_dialog(self.app.mw, self.app.appdata.app_name,
                                     msg)
                return
            self.config.save_dir = str(os.path.dirname(doc_file))
            self.save_config()
            events.emit(events.APP_STATUS, _('Image is successfully saved'))
