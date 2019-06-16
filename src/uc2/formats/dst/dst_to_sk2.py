# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2019 by Maxim S. Barabash
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

from base64 import b64encode
from uc2.formats.dst import dst_model, dst_const
from uc2.formats.sk2 import sk2_model
from uc2 import _, uc2const, sk2const, cms, libgeom

from uc2.libgeom.trafo import apply_trafo_to_point


class EmbroideryMachine(object):

    def __init__(self, dst_doc, sk2_doc, palette=None):
        self.dst_doc = dst_doc
        self.sk2_doc = sk2_doc
        self.palette = palette or dst_doc.palette
        self.sk2_mtds = sk2_doc.methods
        self.x = 0
        self.y = 0
        self.stitch_count = 0
        self.stitch_list = []
        self.rope_width = abs(self.dst_doc.config.thickness or 0.72)
        self.page = self.sk2_mtds.get_page()
        self.hex_color = self.palette.next_color(0)
        self.layer = self.sk2_mtds.get_layer(self.page)
        self.layer.name = self.hex_color
        self.layer.color = self.hex_color

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.stitch_count += 1

    def color_change(self, dx, dy):
        self.move(dx, dy)
        self.end_stitch()

        hex_color = self.palette.next_color()
        layer = self.sk2_mtds.add_layer(self.page, hex_color)
        self.layer = layer
        self.layer.name = hex_color
        self.layer.color = hex_color
        self.hex_color = hex_color

    def stop(self, dx, dy):
        self.move(dx, dy)
        self.end_stitch()

    def stitch(self, dx, dy):
        self.move(dx, dy)
        self.stitch_list.append([self.x, self.y])

    def sequin_eject(self, dx, dy):
        self.move(dx, dy)

    def end_stitch(self):
        if len(self.stitch_list) > 1:
            methods = self.sk2_doc.methods
            path = self.stitch_list
            curve = sk2_model.Curve(
                self.sk2_doc.config,
                parent=None,
                style=self.get_style(),
                paths=[[path[0], path[1:], sk2const.CURVE_OPENED]],
                trafo=[] + dst_const.DST_to_SK2_TRAFO
            )
            methods.append_object(curve, self.layer)
            self.stitch_list = []

    def get_style(self):
        fill = []
        text_style = []
        rgb = cms.hexcolor_to_rgb(self.hex_color)
        color = [uc2const.COLOR_RGB, rgb, 1.0, self.hex_color]
        width = self.rope_width
        stroke = self.get_stroke(color, width)
        return [fill, stroke, text_style, []]

    def get_stroke(self, color, width):
        cap_style = sk2const.CAP_ROUND
        join_style = sk2const.JOIN_ROUND
        rule = sk2const.STROKE_MIDDLE
        dash = []
        miter_limit = 4.0
        behind_flag = 0
        scalable_flag = 0
        markers = [[], []]
        return [rule, width, color, dash, cap_style, join_style, miter_limit,
                behind_flag, scalable_flag, markers]


class DST_to_SK2_Translator(object):
    sk2_mtds = None
    processor = None

    def translate(self, dst_doc, sk2_doc):
        self.processor = EmbroideryMachine(dst_doc, sk2_doc)
        self.sk2_mtds = sk2_doc.methods
        self.walk(dst_doc.model.childs)
        sk2_doc.model.do_update()

    def walk(self, stack):
        sequin_mode = False
        out = self.processor
        for cmd in stack:
            dx, dy = cmd.dx, cmd.dy
            if cmd.cid == dst_const.CMD_STITCH:
                out.stitch(dx, dy)
            elif cmd.cid == dst_const.CMD_JUMP:
                if sequin_mode:
                    out.sequin_eject(dx, dy)  # XXX: didn't check it
                else:
                    out.end_stitch()
                    out.move(dx, dy)
            elif cmd.cid == dst_const.CMD_CHANGE_COLOR:
                out.color_change(dx, dy)
            elif cmd.cid == dst_const.CMD_SEQUIN_MODE:
                out.sequin_mode(dx, dy)  # XXX: didn't check it
                sequin_mode = not sequin_mode
            elif cmd.cid == dst_const.DST_HEADER:
                self.handle_document_header(cmd)
                self.handle_document_metainfo(cmd)
            elif cmd.cid == dst_const.CMD_STOP:
                out.stop(dx, dy)
            else:
                out.move(dx, dy)

        # print 'last x, y', out.x, out.y
        # print 'stitch_count', out.stitch_count

    def handle_document_metainfo(self, rec):
        metainfo = [b'', b'', b'', b'']
        metainfo[3] = b64encode(rec.chunk.split(dst_const.DATA_TERMINATOR)[0])
        self.sk2_mtds.set_doc_metainfo(metainfo)

    def handle_document_header(self, rec):
        height = float(rec.metadata.get('+Y')) + float(rec.metadata.get('-Y'))
        width = float(rec.metadata.get('+X')) + float(rec.metadata.get('-X'))
        width, height = apply_trafo_to_point(
            (width, height),
            dst_const.DST_to_SK2_TRAFO
        )
        orient = uc2const.PORTRAIT
        if width > height:
            orient = uc2const.LANDSCAPE
        page_format = [_('Custom size'), (width, height), orient]

        page = self.sk2_mtds.get_page()
        self.sk2_mtds.set_page_format(page, page_format)

