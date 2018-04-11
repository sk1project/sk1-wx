# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Maxim S. Barabash
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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from datetime import datetime
from collections import defaultdict

import wal
from sk1 import _, config
from uc2 import uc2const, sk2const, libgeom


ORIENTS_NAMES = [_('Portrait'), _('Landscape')]


def pt_to_units(val, units):
    factor = uc2const.point_dict[units]
    accuracy = uc2const.unit_accuracy[units]
    return round(val * factor, accuracy)


class DocInfoDialog(wal.CloseDialog):
    app = None

    def __init__(self, app, parent, title, size=config.docinfo_dlg_size):
        self.app = app
        self.doc = app.current_doc
        wal.CloseDialog.__init__(self, parent, title, size, add_line=False)

    def get_layers(self):
        for page in self.doc.get_pages():
            for layer in self.doc.get_layers(page):
                yield layer
        for layer in self.doc.methods.get_master_layers():
            yield layer

    def get_objects(self, layers=None):
        layers = layers or self.get_layers()
        return (obj for layer in layers for obj in layer.childs)

    def _analyze_path(self, obj, info):
        info['subpaths'] += len(obj.paths)
        for path in libgeom.apply_trafo_to_paths(obj.paths, obj.trafo):
            try:
                info['path_length'] += libgeom.get_path_length(path)
            except RuntimeError:
                info['path_length'] = float('nan')
            if path[2] == sk2const.CURVE_CLOSED:
                info['path_closed'] += 1
                nodes = len(path[1])
            else:
                nodes = len(path[1]) + 1
            info['max_path_point'] = max(nodes, info['max_path_point'])
            info['node'] += nodes

    def _analyze_text(self, obj, info):
        text = obj.get_text()
        lines = text.split('\n')
        words = [word for line in lines for word in line.split()]
        info['line'] += len(lines)
        info['word'] += len(words)
        info['char'] += len(''.join(words))

    def file_info(self, objects):
        doc_name = self.doc.doc_name
        doc_file = self.doc.doc_file
        data = [
            [_('File')],
            [_('Name and location:'), doc_file or doc_name]
        ]
        if doc_file and os.path.lexists(doc_file):
            doc_stat = os.stat(doc_file)
            st_size = '%s bytes' % doc_stat.st_size
            st_mtime = datetime.fromtimestamp(doc_stat.st_mtime).strftime('%c')
            data += [
                [_('File size:'), st_size],
                [_('Modified:'), st_mtime]
            ]
        return data

    def document_info(self, objects):
        pages = self.doc.get_pages()
        layers = list(self.get_layers())
        units = self.doc.model.doc_units
        page_format = self.doc.methods.get_default_page_format()
        width = pt_to_units(page_format[1][0], units)
        height = pt_to_units(page_format[1][1], units)
        page_size = "%s (%s x %s %s)" % (page_format[0], width, height, _(units))
        data = [
            [_('Document')],
            [_('Pages:'), len(pages)],
            [_('Layers:'), len(layers)],
            [_('Page size:'), page_size],
            [_('Page orientation:'), ORIENTS_NAMES[page_format[2]]]
        ]
        return data

    def _walk_objects(self, items, info=None):
        if info is None:
            info = defaultdict(int)
        for obj in items:
            if obj.is_text() or obj.is_pixmap():
                continue
            info['object'] += 1
            if obj.is_curve():
                self._analyze_path(obj, info)
            elif obj.is_rect():
                info['rect'] += 1
            elif obj.is_circle():
                info['circle'] += 1
            elif obj.is_polygon():
                info['polygon'] += 1
            elif obj.is_primitive():
                info['primitive'] += 1
            elif obj.is_container():
                info['container'] += 1
                self._walk_objects(obj.childs, info)
            elif obj.is_group():
                info['group'] += 1
                self._walk_objects(obj.childs, info)
        return info

    def objects_info(self, objects):
        info = self._walk_objects(objects)
        subpaths = info['subpaths']
        closed = info['path_closed']
        opened = info['subpaths'] - info['path_closed']
        units = self.doc.model.doc_units
        path_length = pt_to_units(info['path_length'], units)
        curve_subpaths = _('%i, opened %i, closed %i, length %g %s') % (subpaths, opened, closed, path_length, units)
        data = [
            [_('Graphic Objects')],
            [_('Number of objects:'), info['object']],
            [_('Number of points:'), info['node']],
            [_('Max. # of curve points:'), info['max_path_point']],
            [_('Max. # of curve subpaths:'), curve_subpaths],
            [_('Groups:'), info['group']],
            [_('Rectangles:'), info['rect']],
            [_('Ellipses:'), info['circle']],
            [_('Containers:'), info['container']],
            [_('Polygons:'), info['polygon']]
        ]
        return data

    def _walk_text(self, items, info=None):
        if info is None:
            info = defaultdict(int)
        for obj in items:
            if obj.is_group():
                self._walk_text(obj.childs, info)
            elif obj.is_text() and obj.is_textblock():
                info['textblock'] += 1
                self._analyze_text(obj, info)
                fonts = info.setdefault('font', set())
                fonts.add(obj.style[2][0])
                for markup in obj.markup:
                    if isinstance(markup, tuple) and markup[0][0] == 'font':
                        fonts.add(markup[0][1])
        return info

    def text_info(self, objects):
        info = self._walk_text(objects)
        data = [[_('Text Statistics')]]
        if not info['textblock']:
            data.append([_('No Text in this document.')])
        else:
            data += [
                [_('Artistic text:'), info['textblock']],
                [_('Lines:'), info['line']],
                [_('Words:'), info['word']],
                [_('Characters:'), info['char']]
            ]
            label = _('Fonts used:')
            for font_name in info.get('font', []):
                data.append([label, font_name])
                label = ''
        return data

    def _walk_bitmap(self, items, info=None):
        if info is None:
            info = defaultdict(list)
        for obj in items:
            if obj.is_group():
                self._walk_bitmap(obj.childs, info)
            elif obj.is_pixmap():
                pixmap = info.setdefault('pixmap', [])
                pixmap.append(obj)
        return info

    def bitmap_info(self, objects):
        info = self._walk_bitmap(objects)
        data = [
            [_('Bitmap Objects')],
        ]
        items = info.get('pixmap', [])
        if not items:
            data.append([_('No Bitmaps in this document.')])
        for i in items:
            dpi_w, dpi_h = i.get_resolution()
            val = _('%s (%s x %s dpi), %s bytes') % (i.colorspace, dpi_w, dpi_h, len(i.bitmap))
            data.append(['', val])
        return data

    def _walk_fill(self, items, info=None):
        if info is None:
            info = defaultdict(int)
        color_space = info.setdefault('color_space', defaultdict(int))
        for obj in items:
            if obj.is_pixmap():
                continue
            if obj.is_group():
                self._walk_fill(obj.childs, info)
            else:
                fill_style = obj.style[0]
                space_name = None
                if not fill_style:
                    info['no_fill'] += 1
                elif sk2const.FILL_SOLID == fill_style[1]:
                    info['fill_solid'] += 1
                    space_name = fill_style[2][0]
                elif sk2const.FILL_GRADIENT == fill_style[1]:
                    info['fill_gradient'] += 1
                    space_name = fill_style[2][2][0][1][0]
                elif sk2const.FILL_PATTERN == fill_style[1]:
                    info['fill_pattern'] += 1
                    space_name = fill_style[2][2][0][0]
                if space_name:
                    color_space[space_name] += 1
        return info

    def fill_info(self, objects):
        info = self._walk_fill(objects)
        data = [
            [_('Fills')],
            [_('No fill:'), info['no_fill']],
            [_('Solid:'), info['fill_solid']],
            [_('Gradients:'), info['fill_gradient']],
            [_('Patterns:'), info['fill_pattern']],
            [_('Objects and Color models')]
        ]
        color_space = info['color_space']
        for space_name in color_space:
            data.append(['\t%s' % space_name, color_space[space_name]])
        return data

    def _walk_stroke(self, items, info=None):
        if info is None:
            info = defaultdict(int)
        color_space = info.setdefault('color_space', defaultdict(int))
        for obj in items:
            if obj.is_pixmap():
                continue
            if obj.is_group():
                self._walk_stroke(obj.childs, info)
            else:
                stroke_style = obj.style[1]
                space_name = None
                if not stroke_style:
                    info['no_stroke'] += 1
                else:
                    info['stroke_solid'] += 1
                    space_name = stroke_style[2][0]
                if space_name:
                    color_space[space_name] += 1
        return info

    def stroke_info(self, objects):
        info = self._walk_stroke(objects)
        data = [
            [_('Strokes')],
            [_('No stroke:'), info['no_stroke']],
            [_('Solid:'), info['stroke_solid']],
            [_('Objects and Color models')]
        ]
        color_space = info['color_space']
        for space_name in color_space:
            data.append(['\t%s' % space_name, color_space[space_name]])
        return data

    def build(self):
        block = []
        data = [[_('Property'), _('Value')]]
        r = ['file_info', 'document_info', 'objects_info', 'text_info',
             'bitmap_info', 'fill_info', 'stroke_info']
        for item in r:
            block.append(len(data) - 1)
            data += getattr(self, item)(self.get_objects())
        slist = wal.ReportList(self, data, alt_color=False)
        for idx in block:
            list_item = slist.GetItem(idx)
            list_item.SetBackgroundColour(slist.even_color)
            slist.SetItem(list_item)
        self.pack(slist, expand=True, fill=True, padding_all=5)


def docinfo_dlg(app, parent):
    title = _('Document info')
    dlg = DocInfoDialog(app, parent, title)
    dlg.Refresh()
    dlg.show()
