# -*- coding: utf-8 -*-
#
#  Copyright (C) 2019 by Maxim S. Barabash
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

from uc2.formats.xar import xar_model, xar_const
from uc2.formats.sk2 import sk2_model
from uc2 import libimg
from uc2.libgeom import multiply_trafo, get_point_angle, trafo_rotate
from uc2.libgeom import trafo_rotate_grad
from uc2.libgeom.points import distance, is_equal_points
from uc2.libgeom.trafo import apply_trafo_to_points, apply_trafo_to_point
from uc2.libgeom.bbox import bbox_to_rect
from uc2 import _, uc2const, sk2const, cms
from colorsys import hsv_to_rgb, rgb_to_hsv
from base64 import b64decode, b64encode
import copy
import math


XAR_TO_SK2_UNITS = {
    xar_const.REF_UNIT_PIXELS: uc2const.UNIT_PX,
    xar_const.REF_UNIT_MILLIMETRES: uc2const.UNIT_MM,
    xar_const.REF_UNIT_CENTIMETRES: uc2const.UNIT_CM,
    xar_const.REF_UNIT_METRES: uc2const.UNIT_M,
    xar_const.REF_UNIT_INCHES: uc2const.UNIT_IN,
    xar_const.REF_UNIT_FEET: uc2const.UNIT_FT,
}

XAR_TO_SK2_FILL_REPEATING = {
    xar_const.TAG_FILL_REPEATING: sk2const.GRADIENT_EXTEND_PAD,
    xar_const.TAG_FILL_NONREPEATING: sk2const.GRADIENT_EXTEND_NONE,
    xar_const.TAG_FILL_REPEATINGINVERTED: sk2const.GRADIENT_EXTEND_REFLECT,
    xar_const.TAG_FILL_REPEATING_EXTRA: sk2const.GRADIENT_EXTEND_REPEAT,
}

XAR_TO_SK2_CAP = {
    xar_const.CAP_BUTT: sk2const.CAP_BUTT,
    xar_const.CAP_ROUND: sk2const.CAP_ROUND,
    xar_const.CAP_SQUARE: sk2const.CAP_SQUARE,
}

XAR_TO_SK2_JOIN = {
    xar_const.JOIN_BEVEL: sk2const.JOIN_BEVEL,
    xar_const.JOIN_MITRE: sk2const.JOIN_MITER,
    xar_const.JOIN_ROUND: sk2const.JOIN_ROUND
}

XAR_TO_SK2_WINDING = {
    xar_const.FILL_EVENODD: sk2const.FILL_EVENODD,
    xar_const.FILL_NONZERO: sk2const.FILL_NONZERO
}

XAR_TO_SK2_TEXT_ALIGN = {
    xar_const.TEXT_ALIGN_LEFT: sk2const.TEXT_ALIGN_LEFT,
    xar_const.TEXT_ALIGN_CENTRE: sk2const.TEXT_ALIGN_CENTER,
    xar_const.TEXT_ALIGN_RIGHT: sk2const.TEXT_ALIGN_RIGHT,
    xar_const.TEXT_ALIGN_FULL: sk2const.TEXT_ALIGN_JUSTIFY
}

MODE_TINT = {
    uc2const.COLOR_RGB: xar_const.RGB_WHITE,
    uc2const.COLOR_CMYK: xar_const.CMYK_WHITE,
    uc2const.COLOR_GRAY: xar_const.GREYSCALE_WHITE,
}

TEXT_ALIGN_NEED_FIX = [xar_const.TEXT_ALIGN_CENTRE, xar_const.TEXT_ALIGN_RIGHT]

RAINBOW_EFFECT = [
    xar_const.TAG_FILLEFFECT_RAINBOW,
    xar_const.TAG_FILLEFFECT_ALTRAINBOW
]


def color_tint(color1, coef=0.5, colour_name=''):
    mode = color1[0]
    color2 = MODE_TINT.get(mode)
    if color2 is not None:
        colour = cms.mix_lists(color2[1], color1[1], coef)
        a = cms.mix_vals(color2[2], color1[2], coef)
        return [mode, colour, a, colour_name]
    raise NotImplemented()


def pick_page_format_name(width, height):
    if width > height:
        size = (height, width)
    else:
        size = (width, height)
    for name, fzise in uc2const.PAGE_FORMATS.items():
        if is_equal_points(fzise, size, 2):
            return name
    return _('Custom')


def make_trafo(centre_point, major_axes, minor_axes, trafo):
    width = distance(major_axes, centre_point)
    c = distance(minor_axes, centre_point)
    cx, cy = apply_trafo_to_point(centre_point, trafo)

    angle1 = get_point_angle(major_axes, centre_point)
    angle2 = get_point_angle(minor_axes, centre_point)
    angle = abs(angle2 - angle1)
    height = c * math.sin(angle)
    tr = [width, 0.0, 0.0, height, cx, cy]
    tr_rotate = trafo_rotate(angle1, cx, cy)
    tr = multiply_trafo(tr, tr_rotate)
    return tr



class XAR_to_SK2_Translator(object):
    xar_doc = None
    xar_mtds = None
    sk2_doc = None
    sk2_model = None
    sk2_mtds = None

    fontmap = None
    bitmaps = None
    colors = None
    atomic_tags = None

    buffer_text = None
    buffer_text_line = None
    stack_style = None
    stack = None
    pages = None
    layers = None

    style = None
    trafo = None

    layer = None
    layer_name = ''
    layer_flags = None
    page_name = ''
    page_format = None
    _handler = None
    debug_flag = True

    def translate(self, xar_doc, sk2_doc):
        self._handler = {}
        self.xar_doc = xar_doc
        self.xar_mtds = xar_doc.methods
        self.sk2_doc = sk2_doc
        self.sk2_model = sk2_doc.model
        self.sk2_mtds = sk2_doc.methods
        self.sk2_mtds.delete_page()

        self.bitmaps = {}
        self.colors = copy.deepcopy(xar_const.XAR_COLOURS)
        self.atomic_tags = set()
        self.trafo = [-1.0, 0.0, 0.0, -1.0, 0.0, 0.0]

        self.buffer_text = []
        self.buffer_text_line = []
        self.stack = []
        self.stack_style = [copy.copy(xar_const.XAR_DEFAULT_STYLE)]
        self.pages = []
        self.layers = []

        self.walk(xar_doc.model.childs[::-1])
        self.handle_endoffile()
        if self.debug_flag:
            with open(self.sk2_doc.doc_file+".txt", 'w') as f:
                f.write(str(sorted(list(self.atomic_tags))))
        sk2_doc.model.do_update()

    def walk(self, stack):
        while stack:
            rec = stack.pop()
            if not self.is_atomic(rec.cid):
                if rec.childs:
                    childs = rec.childs[::-1]
                    rec.childs = []
                    stack.append(childs[0])
                    stack.append(rec)
                    stack.extend(childs[1:])
                else:
                    self.process(rec)

    def is_atomic(self, cid):
        if cid in self.atomic_tags:
            return True
        elif cid not in xar_const.XAR_TYPE_RECORD:
            self.atomic_tags.add(cid)
            return True

    def process(self, rec):
        handler = self._handler.get(rec.cid)
        if not handler:
            rec_type = xar_const.XAR_TYPE_RECORD.get(rec.cid, {})
            name = rec_type.get('name')
            handler_name = 'handle_%s' % name.lower().replace(' ', '_')
            handler = getattr(self, handler_name, None)
            if handler:
                self._handler[rec.cid] = handler

        if handler:
            handler(rec, self.sk2_doc.config)
        else:
            self.atomic_tags.add(rec.cid)

    def handle_previewbitmap_gif(self, rec, cfg):
        if self.debug_flag:
            fn = self.sk2_doc.doc_file.rsplit('.', 1)[0]
            with open(fn + '.gif', 'wb') as f:
                f.write(rec.chunk)

    def handle_previewbitmap_jpeg(self, rec, cfg):
        if self.debug_flag:
            fn = self.sk2_doc.doc_file.rsplit('.', 1)[0]
            with open(fn + '.jpeg', 'wb') as f:
                f.write(rec.chunk)

    def handle_previewbitmap_png(self, rec, cfg):
        if self.debug_flag:
            fn = self.sk2_doc.doc_file.rsplit('.', 1)[0]
            with open(fn + '.png', 'wb') as f:
                f.write(rec.chunk)

    # Navigation records
    def handle_up(self, rec, cfg):
        self.style = self.stack_style.pop()

    def handle_down(self, rec, cfg):
        self.style = copy.copy(self.stack_style[-1])
        self.stack_style.append(self.style)

    def handle_fileheader(self, rec, cfg): pass

    def handle_endoffile(self, rec=None, cfg=None):
        parent = self.sk2_mtds.get_pages_obj()
        if self.stack or not self.pages and not parent.childs:
            cfg = cfg or self.sk2_doc.config
            self.handle_layer(rec, cfg)
            self.handle_spread(rec, cfg)

        self.pages = [page for page in self.pages if page.childs]
        for page in self.pages:
            page.parent = parent
        parent.page_counter += len(self.pages)
        parent.childs.extend(self.pages)
        self.pages = []

    # Tag management
    def handle_atomictags(self, rec, cfg): pass

    def handle_essentialtags(self, rec, cfg): pass

    def handle_tagdescription(self, rec=None, cfg=None):
        if self.debug_flag:
            for item in rec.description:
                if item[0] not in xar_const.XAR_TYPE_RECORD:
                    print("# xar tagdescription %s" % item)

    # Compression tags
    def handle_startcompression(self, rec, cfg): pass

    def handle_endcompression(self, rec, cfg): pass

    # Document tags
    def handle_document(self, rec, cfg): pass

    def handle_chapter(self, rec, cfg): pass

    def handle_spread(self, rec, cfg):
        page = sk2_model.Page(cfg, name=self.page_name)
        if self.page_format:
            page.page_format = self.page_format
        self.page_name = ''

        for el in self.layers:
            el.parent = page

        page.layer_counter += len(self.layers)
        page.childs.extend(self.layers)
        self.layers = []
        self.pages.append(page)

    # Notes
    def handle_layer(self, rec, cfg):
        is_antialiased = True
        layer = sk2_model.Layer(cfg, name=self.layer_name)
        if self.layer_flags is not None:
            layer.properties = [
                self.layer_flags.is_visible,
                not self.layer_flags.is_locked,
                self.layer_flags.is_printable,
                is_antialiased
            ]
            # TODO: set active layer
            # if self.layer_flags.is_active:
            #     self.sk2_doc.active_layer = layer
            self.layer_flags = None
        self.layer_name = ''
        self.flush_stack(layer)
        self.layers.append(layer)

    def handle_page(self, rec, cfg): pass

    def handle_spreadinformation(self, rec, cfg):
        width = rec.width
        height = rec.height
        fmt = pick_page_format_name(width, height)
        size = (width, height)
        orient = uc2const.PORTRAIT
        if width > height:
            orient = uc2const.LANDSCAPE
        self.page_format = [fmt, size, orient]
        trafo = [1.0, 0.0, 0.0, 1.0, -1.0 * width / 2.0, -1.0 * height / 2.0]
        self.set_trafo(trafo)

#    def handle_gridrulersettings(self, rec, cfg): pass
#    def handle_gridrulerorigin(self, rec, cfg): pass

    def handle_layerdetails(self, rec, cfg):
        self.layer_flags = rec.layer_flags
        self.layer_name = rec.layer_name

#    def handle_guidelayerdetails(self, rec, cfg): pass
#    def handle_spreadscaling_active(self, rec, cfg): pass
#    def handle_spreadscaling_inactive(self, rec, cfg): pass

    # Colour reference tags
    def handle_definergbcolour(self, rec, cfg):
        rgb = cms.val_255_to_dec([rec.red, rec.green, rec.blue])
        name = cms.rgb_to_hexcolor(rgb)
        colour = [uc2const.COLOR_RGB, rgb, 1.0, name]
        self.colors[rec.idx] = colour

    def handle_definecomplexcolour(self, rec, cfg):
        colour = None

        if rec.colour_type == xar_const.COLOUR_TYPE_NORMAL:
            if rec.colour_model == xar_const.COLOUR_MODEL_GREYSCALE:
                grey = [rec.component1]
                colour = [uc2const.COLOR_GRAY, grey, 1.0, rec.colour_name]
            elif rec.colour_model == xar_const.COLOUR_MODEL_RGB:
                rgb = [rec.component1, rec.component2, rec.component3]
                colour = [uc2const.COLOR_RGB, rgb, 1.0, rec.colour_name]
            elif rec.colour_model == xar_const.COLOUR_MODEL_HSV:
                rgb = hsv_to_rgb(rec.component1, rec.component2, rec.component3)
                colour = [uc2const.COLOR_RGB, list(rgb), 1.0, rec.colour_name]
            elif rec.colour_model == xar_const.COLOUR_MODEL_CMYK:
                cmyk = [rec.component1, rec.component2,
                        rec.component3, rec.component4]
                colour = [uc2const.COLOR_CMYK, cmyk, 1.0, rec.colour_name]
        elif rec.colour_type == xar_const.COLOUR_TYPE_SPOT:
            pass  # TODO
        elif rec.colour_type == xar_const.COLOUR_TYPE_TINT:
            parent_color = self.get_color(rec.parent_colour)
            colour = color_tint(parent_color, rec.component1, rec.colour_name)
        elif rec.colour_type == xar_const.COLOUR_TYPE_LINKED:
            pass  # TODO
        elif rec.colour_type == xar_const.COLOUR_TYPE_SHADE:
            pass  # TODO

        if not colour:
            # TODO: process colour_model, colour_type
            rgb = cms.hexcolor_to_rgb(b"#%s" % rec.rgbcolor)
            colour = [uc2const.COLOR_RGB, rgb, 1.0, rec.colour_name]

        self.colors[rec.idx] = colour

    # Bitmap reference tags
    def handle_definebitmap_jpeg(self, rec, cfg):
        self.bitmaps[rec.idx] = rec.bitmap_data

    def handle_definebitmap_png(self, rec, cfg):
        self.bitmaps[rec.idx] = rec.bitmap_data

#    def handle_definebitmap_jpeg8BPP = 71

    # View tags
#    def handle_viewport(self, rec, cfg): pass
#    def handle_viewquality(self, rec, cfg): pass
#    def handle_documentview(self, rec, cfg): pass

    # Document unit tags
#    def handle_define_prefixuserunit(self, rec, cfg): pass
#    def handle_define_suffixuserunit(self, rec, cfg): pass
#    def handle_define_defaultunits(self, rec, cfg): pass

    # Document info tags
    def handle_documentcomment(self, rec, cfg):
        metainfo = [b'', b'', b'', b'']
        metainfo[3] = b64encode(rec.comment)
        self.sk2_mtds.set_doc_metainfo(metainfo)

#    def handle_documentdates(self, rec, cfg): pass
#    def handle_documentundosize(self, rec, cfg): pass

    def handle_documentflags(self, rec, cfg): pass
        # print 'documentflags', self.sk2_doc.doc_file
        # print rec.document_flags

#    def handle_documentinformation(self, rec, cfg): pass

    # Object tags
    def handle_path(self, rec, cfg):
        curve = sk2_model.Curve(
            cfg, None,
            self.get_path(rec),
            self.get_trafo(),
            self.get_style()
        )
        self.stack.append(curve)

    def handle_path_filled(self, rec, cfg):
        curve = sk2_model.Curve(
            cfg, None,
            self.get_path(rec),
            self.get_trafo(),
            self.get_style(fill=True)
        )
        curve.fill_trafo = self.get_fill_trafo()
        self.stack.append(curve)

    def handle_path_strokedled(self, rec, cfg):
        curve = sk2_model.Curve(
            cfg, None,
            self.get_path(rec),
            self.get_trafo(),
            self.get_style(stroke=True)
        )
        self.stack.append(curve)

    def handle_path_filled_stroked(self, rec, cfg):
        curve = sk2_model.Curve(
            cfg, None,
            self.get_path(rec),
            self.get_trafo(),
            self.get_style(stroke=True, fill=True)
        )
        curve.fill_trafo = self.get_fill_trafo()
        self.stack.append(curve)

    def handle_group(self, rec, cfg):
        if self.stack and len(self.stack) > 1:
            group = sk2_model.Group(cfg)
            self.flush_stack(group)
            self.stack = [group]

    def handle_blend(self, rec, cfg):
        # TODO: implement this
        pass

#    def handle_blender(self, rec, cfg): pass
#    def handle_mould_envelope(self, rec, cfg): pass
#    def handle_mould_perspective(self, rec, cfg): pass
#    def handle_mould_group(self, rec, cfg): pass
#    def handle_mould_path(self, rec, cfg): pass
#    def handle_path_flags(self, rec, cfg): pass
#    def handle_guideline(self, rec, cfg): pass
    def handle_path_relative(self, rec, cfg):
        curve = sk2_model.Curve(
            cfg, None,
            self.get_path_relative(rec),
            self.get_trafo(),
            self.get_style()
        )
        self.stack.append(curve)

    def handle_path_relative_filled(self, rec, cfg):
        curve = sk2_model.Curve(
            cfg, None,
            self.get_path_relative(rec),
            self.get_trafo(),
            self.get_style(fill=True)
        )
        curve.fill_trafo = self.get_fill_trafo()
        self.stack.append(curve)

    def handle_path_relative_stroked(self, rec, cfg):
        curve = sk2_model.Curve(
            cfg, None,
            self.get_path_relative(rec),
            self.get_trafo(),
            self.get_style(stroke=True)
        )
        self.stack.append(curve)

    def handle_path_relative_filled_stroked(self, rec, cfg):
        curve = sk2_model.Curve(
            cfg, None,
            self.get_path_relative(rec),
            self.get_trafo(),
            self.get_style(stroke=True, fill=True)
        )
        curve.fill_trafo = self.get_fill_trafo()
        self.stack.append(curve)

#    def handle_pathref_transform(self, rec, cfg): pass

    # Attribute tags
    def handle_flatfill(self, rec, cfg):
        colour = self.colors.get(rec.colour)
        if colour:
            self.style['flat_colour_fill'] = colour

    def handle_linecolour(self, rec, cfg):
        colour = self.colors.get(rec.colour)
        if colour:
            self.style['stroke_colour'] = colour

    def handle_linewidth(self, rec, cfg):
        self.style['line_width'] = rec.width

    def handle_linearfill(self, rec, cfg):
        trafo = self.get_trafo()
        points = [rec.start_point, rec.end_point]
        vector = apply_trafo_to_points(points, trafo)
        start_colour = self.get_color(rec.start_colour)
        end_colour = self.get_color(rec.end_colour)
        stops = [[0.0, start_colour], [1.0, end_colour]]
        self.style['gradient_fill'] = [
            sk2const.GRADIENT_LINEAR,
            vector,
            stops,
            sk2const.GRADIENT_EXTEND_PAD  # TODO
        ]

    def handle_circularfill(self, rec, cfg):
        trafo = self.get_trafo()
        points = [rec.centre_point, rec.edge_point]
        vector = apply_trafo_to_points(points, trafo)
        start_colour = self.get_color(rec.start_colour)
        end_colour = self.get_color(rec.end_colour)
        stops = [[0.0, start_colour], [1.0, end_colour]]
        self.style['gradient_fill'] = [
            sk2const.GRADIENT_RADIAL,
            vector,
            stops,
            sk2const.GRADIENT_EXTEND_PAD  # TODO
        ]

    def handle_ellipticalfill(self, rec, cfg):
        trafo = self.get_trafo()
        start_colour = self.get_color(rec.start_colour)
        end_colour = self.get_color(rec.end_colour)
        stops = [[0.0, start_colour], [1.0, end_colour]]

        self.style['gradient_fill'] = [
            sk2const.GRADIENT_RADIAL,
            [[0.0, 0.0], [1.0, 0.0]],
            stops,
            sk2const.GRADIENT_EXTEND_PAD  # TODO
        ]
        tr = make_trafo(rec.centre_point, rec.major_axes, rec.minor_axes, trafo)
        self.style['fill_trafo'] = tr

#    def handle_conicalfill(self, rec, cfg): pass

    def handle_bitmapfill(self, rec, cfg):
        # TODO:  rotation, skew of pattern
        image_str = self.bitmaps.get(rec.bitmap)
        if image_str is None:
            return
        ptrn, flag = libimg.read_pattern(image_str)
        ptrn_type = sk2const.PATTERN_TRUECOLOR
        angle1 = get_point_angle(rec.bottom_right, rec.bottom_left)
        trafo1 = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        trafo2 = trafo_rotate(angle1)
        ptrn_trafo = multiply_trafo(trafo1, trafo2)
        ptrn_transf = [1.0, 1.0, 0.0, 0.0, angle1]
        ptrn_style = [copy.deepcopy(sk2const.RGB_BLACK),
                      copy.deepcopy(sk2const.RGB_WHITE)]
        pattern = [ptrn_type, ptrn, ptrn_style, ptrn_trafo, ptrn_transf]
        self.style['pattern_fill'] = pattern

#    def handle_contonebitmapfill(self, rec, cfg): pass
#    def handle_fractalfill(self, rec, cfg): pass
    def handle_filleffect_fade(self, rec, cfg):
        # print self.sk2_doc.doc_file, rec.cid
        self.style['fill_effect'] = rec.cid

    def handle_filleffect_rainbow(self, rec, cfg):
        # print self.sk2_doc.doc_file,rec.cid
        self.style['fill_effect'] = rec.cid

    def handle_filleffect_altrainbow(self, rec, cfg):
        # print self.sk2_doc.doc_file,rec.cid
        self.style['fill_effect'] = rec.cid

    def handle_fill_repeating(self, rec, cfg):
        self.style['fill_repeating'] = rec.cid

    def handle_fill_nonrepeating(self, rec, cfg):
        self.style['fill_repeating'] = rec.cid

    def handle_fill_repeatinginverted(self, rec, cfg):
        self.style['fill_repeating'] = rec.cid

#    def handle_flattransparentfill(self, rec, cfg): pass
#    def handle_lineartransparentfill(self, rec, cfg): pass
#    def handle_circulartransparentfill(self, rec, cfg): pass
#    def handle_ellipticaltransparentfill(self, rec, cfg): pass
#    def handle_conicaltransparentfill(self, rec, cfg): pass
#    def handle_bitmaptransparentfill(self, rec, cfg): pass
#    def handle_fractaltransparentfill(self, rec, cfg): pass
#    def handle_linetransparency(self, rec, cfg): pass

    def handle_startcap(self, rec, cfg):
        self.style['start_cap'] = rec.cap_style

    def handle_joinstyle(self, rec, cfg):
        self.style['join_type'] = rec.join_style

    def handle_mitrelimit(self, rec, cfg):
        self.style['mitre_limit'] = rec.mitre_limit

    def handle_windingrule(self, rec, cfg):
        self.style['winding_rule'] = rec.winding_rule

#    def handle_quality(self, rec, cfg): pass

#    def handle_transparentfill_repeating(self, rec, cfg): pass
#    def handle_transparentfill_nonrepeating(self, rec, cfg): pass
#    def handle_transparentfill_repeatinginverted(self, rec, cfg): pass

    # Arrows and dash patterns
#    def handle_dashstyle(self, rec, cfg): pass
#    def handle_definedash(self, rec, cfg): pass
#    def handle_arrowhead(self, rec, cfg): pass
#    def handle_arrowtail(self, rec, cfg): pass
#    def handle_definearrow(self, rec, cfg): pass
#    def handle_definedash_scaled(self, rec, cfg): pass

    # User Attributes
#    def handle_uservalue(self, rec, cfg): pass

    # special colour fills
    def handle_flatfill_none(self, rec, cfg):
        self.style['flat_colour_fill'] = None

    def handle_flatfill_black(self, rec, cfg):
        self.style['flat_colour_fill'] = xar_const.RGB_BLACK

    def handle_flatfill_white(self, rec, cfg):
        self.style['flat_colour_fill'] = xar_const.RGB_WHITE

    def handle_linecolour_none(self, rec, cfg):
        self.style['stroke_colour'] = None

    def handle_linecolour_black(self, rec, cfg):
        self.style['stroke_colour'] = xar_const.RGB_BLACK

    def handle_linecolour_white(self, rec, cfg):
        self.style['stroke_colour'] = xar_const.RGB_WHITE

    # Bitmaps
    def handle_node_bitmap(self, rec, cfg):
        image_str = self.bitmaps.get(rec.bitmap)
        if image_str is None:
            return

        el = sk2_model.Pixmap(cfg, None, bitmap=image_str)
        # XXX: extract alpha channel from image looks very dirty
        el.handler.load_from_images(self.sk2_doc.cms, el.handler.bitmap)
        el.handler.invert_alpha()
        w, h = el.size

        w1 = distance(rec.bottom_left, rec.bottom_right)
        h1 = distance(rec.bottom_left, rec.top_left)
        angle1 = get_point_angle(rec.bottom_right, rec.bottom_left)

        tr1 = trafo_rotate(angle1)
        tr2 = [w1/w, 0.0, 0.0, h1/h, rec.top_left[0], rec.top_left[1]]
        tr = multiply_trafo(tr1, tr2)
        el.trafo = multiply_trafo(tr, self.get_trafo())
        self.stack.append(el)

#    def handle_node_contonedbitmap(self, rec, cfg): pass

    # New fill type records
#    def handle_diamondfill(self, rec, cfg): pass
#    def handle_diamondtransparentfill(self, rec, cfg): pass
#    def handle_threecolfill(self, rec, cfg): pass
#    def handle_threecoltransparentfill(self, rec, cfg): pass
#    def handle_fourcolfill(self, rec, cfg): pass
#    def handle_fourcoltransparentfill(self, rec, cfg): pass

    def handle_fill_repeating_extra(self, rec, cfg):
        self.style['fill_repeating'] = rec.cid

#   def handle_transparentfill_repeating_extra(self, rec, cfg): pass

    # Regular shapes
    # Ellipses
    def handle_ellipse_simple(self, rec, cfg):
        h = rec.height
        w = rec.width
        cx, cy = rec.centre
        el = sk2_model.Circle(
            cfg, None,
            rect=[-w/2.0, -h/2.0, w, h],
            angle1=0.0,
            angle2=0.0,
            circle_type=sk2const.ARC_CHORD,
            style=self.get_style(fill=True, stroke=True)
        )
        tr = [1.0, 0.0, 0.0, 1.0, cx, cy]
        el.trafo = multiply_trafo(el.trafo, tr)
        el.trafo = multiply_trafo(el.trafo, self.get_trafo())
        el.fill_trafo = self.get_fill_trafo()
        self.stack.append(el)

    def handle_ellipse_complex(self, rec, cfg):
        el = sk2_model.Circle(
            cfg, None,
            style=self.get_style(fill=True, stroke=True)
        )
        cx, cy = rec.centre
        el.trafo = make_trafo(
            [0, 0], rec.major_axis, rec.minor_axis,
            [1.0, 0.0, 0.0, 1.0, cx, cy]
        )
        el.trafo = multiply_trafo(el.trafo, self.get_trafo())
        el.fill_trafo = self.get_fill_trafo()
        self.stack.append(el)

    # Rectangles
#    def handle_rectangle_simple(self, rec, cfg): pass
#    def handle_rectangle_simple_rounded(self, rec, cfg): pass
#    def handle_rectangle_complex(self, rec, cfg): pass
#    def handle_rectangle_complex_rounded(self, rec, cfg): pass

    # Polygons
#    def handle_polygon_complex(self, rec, cfg): pass
#    def handle_polygon_complex_rounded(self, rec, cfg): pass
#    def handle_polygon_complex_rounded_reformed(self, rec, cfg): pass
#    def handle_polygon_complex_rounded_stellated(self, rec, cfg): pass

    # General regular shapes
#    def handle_regular_shape_phase_1(self, rec, cfg): pass

    def handle_regular_shape_phase_2(self, rec, cfg):
        w = distance(rec.minor_axes)
        h = distance(rec.major_axes)

        if rec.flags == 1:
            el = sk2_model.Circle(
                cfg, None,
                rect=[-w, -h, w*2.0, h*2.0],
                angle1=0.0,
                angle2=0.0,
                circle_type=sk2const.ARC_CHORD,
                style=self.get_style(fill=True, stroke=True)
            )
        else:
            el = sk2_model.Polygon(
                cfg, None,
                corners_num=rec.number_of_sides,
                coef2=rec.stell_radius_to_primary if rec.flags & 2 else 1.0,
                style=self.get_style(fill=True, stroke=True)
            )
            angle = -90 + 360.0 / rec.number_of_sides / 2.0
            tr = trafo_rotate_grad(angle, 0.5, 0.5)
            el.trafo = multiply_trafo(el.trafo, tr)
            tr = [w*2.0, 0.0, 0.0, h*2.0, -w, -h]
            el.trafo = multiply_trafo(el.trafo, tr)

        tr = [rec.a, rec.b, rec.c, rec.d, rec.e/1000.0, rec.f/1000.0]
        el.trafo = multiply_trafo(el.trafo, tr)
        el.trafo = multiply_trafo(el.trafo, self.get_trafo())
        el.fill_trafo = self.get_fill_trafo()
        self.stack.append(el)

    # Text related records
    # Text definitions
    def handle_font_def_truetype(self, rec, cfg):
        self.style['text_font_family'] = rec.typeface_name

#    def handle_font_def_atm(self, rec, cfg): pass

    # vanilla text story objects
    def handle_text_story_simple(self, rec, cfg):
        text = b'\n'.join(self.buffer_text)
        self.buffer_text = []
        point = apply_trafo_to_point(rec.anchor, self.trafo)
        el = sk2_model.Text(
            cfg,
            point=point,
            text=text,
            style=self.get_text_style()
        )
        # el = self.correct_text_basepoint(el)
        el.fill_trafo = self.get_fill_trafo()
        self.stack.append(el)

    def handle_text_story_complex(self, rec, cfg):
        text = b'\n'.join(self.buffer_text)
        self.buffer_text = []
        tr = [rec.a, rec.b, rec.c, rec.d, rec.e/1000.0, rec.f/1000.0]
        trafo = multiply_trafo(tr, self.get_trafo())
        el = sk2_model.Text(
            cfg,
            text=text,
            style=self.get_text_style(),
            trafo=trafo
        )
        # el = self.correct_text_basepoint(el)
        el.fill_trafo = self.get_fill_trafo()
        self.stack.append(el)

    def correct_text_basepoint(self, text_element):
        text_justification = self.style['text_justification']
        if text_justification in TEXT_ALIGN_NEED_FIX:
            text_element.update()
            rect = bbox_to_rect(text_element.cache_bbox)
            shift = rect[2]
            if text_justification == xar_const.TEXT_ALIGN_CENTRE:
                shift /= 2.0
            text_element.trafo[4] += shift
        return text_element

    # text story objects on a path
#    def handle_text_story_simple_start_left(self, rec, cfg): pass
#    def handle_text_story_simple_start_right(self, rec, cfg): pass
#    def handle_text_story_simple_end_left(self, rec, cfg): pass
#    def handle_text_story_simple_end_right(self, rec, cfg): pass
#    def handle_text_story_complex_start_left(self, rec, cfg): pass
#    def handle_text_story_complex_start_right(self, rec, cfg): pass
#    def handle_text_story_complex_end_left(self, rec, cfg): pass
#    def handle_text_story_complex_end_right(self, rec, cfg): pass

    # Text story information records
#    def handle_text_story_word_wrap_info(self, rec, cfg): pass
#    def handle_text_story_indent_info(self, rec, cfg): pass

    # other text story related objects
    def handle_text_line(self, rec, cfg):
        if self.buffer_text_line:
            line = b''.join(self.buffer_text_line)
            self.buffer_text_line = []
            self.buffer_text.append(line)

    def handle_text_string(self, rec, cfg):
        string = rec.chunk.decode('utf_16_le').encode('utf-8')
        self.buffer_text_line.append(string)

    def handle_text_char(self, rec, cfg):
        self.handle_text_string(rec, cfg)

    def handle_text_eol(self, rec, cfg):
        self.handle_text_line(rec, cfg)

#    def handle_text_kern(self, rec, cfg): pass
#    def handle_text_caret(self, rec, cfg): pass
#    def handle_text_line_info(self, rec, cfg): pass

    # Text attributes
#    def handle_text_linespace_ratio(self, rec, cfg): pass
#    def handle_text_linespace_absolute(self, rec, cfg): pass
    def handle_text_justification_left(self, rec, cfg):
        self.style['text_justification'] = xar_const.TEXT_ALIGN_LEFT

    def handle_text_justification_centre(self, rec, cfg):
        self.style['text_justification'] = xar_const.TEXT_ALIGN_CENTRE

    def handle_text_justification_right(self, rec, cfg):
        self.style['text_justification'] = xar_const.TEXT_ALIGN_RIGHT

    def handle_text_justification_full(self, rec, cfg):
        self.style['text_justification'] = xar_const.TEXT_ALIGN_FULL

    def handle_text_font_size(self, rec, cfg):
        self.style['text_script_size'] = rec.font_size * 0.7  # XXX

#    def handle_text_font_typeface(self, rec, cfg): pass
#    def handle_text_bold_on(self, rec, cfg): pass
#    def handle_text_bold_off(self, rec, cfg): pass
#    def handle_text_italic_on(self, rec, cfg): pass
#    def handle_text_italic_off(self, rec, cfg): pass
#    def handle_text_underline_on(self, rec, cfg): pass
#    def handle_text_underline_off(self, rec, cfg): pass
#    def handle_text_script_on(self, rec, cfg): pass
#    def handle_text_script_off(self, rec, cfg): pass
#    def handle_text_superscript_on(self, rec, cfg): pass
#    def handle_text_subscript_on(self, rec, cfg): pass
#    def handle_text_tracking(self, rec, cfg): pass
#    def handle_text_aspect_ratio(self, rec, cfg): pass
#    def handle_text_baseline(self, rec, cfg): pass

    # Imagesetting attributes
#    def handle_overprintlineon(self, rec, cfg): pass
#    def handle_overprintlineoff(self, rec, cfg): pass
#    def handle_overprintfillon(self, rec, cfg): pass
#    def handle_overprintfilloff(self, rec, cfg): pass
#    def handle_printonallplateson(self, rec, cfg): pass
#    def handle_printonallplatesoff(self, rec, cfg): pass

    # Document Print/Imagesetting options
#    def handle_printersettings(self, rec, cfg): pass
#    def handle_imagesetting(self, rec, cfg): pass
#    def handle_colourplate(self, rec, cfg): pass

    # Registration mark records
#    def handle_printmarkdefault(self, rec, cfg): pass

    # Stroking records
#    def handle_variablewidthfunc(self, rec, cfg): pass
#    def handle_variablewidthtable(self, rec, cfg): pass
#    def handle_stroketype(self, rec, cfg): pass
#    def handle_strokedefinition(self, rec, cfg): pass
#    def handle_strokeairbrush(self, rec, cfg): pass

    # Fractal Noise records
#    def handle_noisefill(self, rec, cfg): pass
#    def handle_noisetransparentfill(self, rec, cfg): pass

    # Mould bounds record
#    def handle_mould_bounds(self, rec, cfg): pass

    # Bitmap export hint record
#    def handle_export_hint(self, rec, cfg): pass

    # Web Address tags
#    def handle_webaddress(self, rec, cfg): pass
#    def handle_webaddress_boundingbox(self, rec, cfg): pass

    # Frame layer tags
#    def handle_layer_frameprops(self, rec, cfg): pass
#    def handle_spread_animprops(self, rec, cfg): pass

    # Wizard properties tags
#    def handle_wizop(self, rec, cfg): pass
#    def handle_wizop_style(self, rec, cfg): pass
#    def handle_wizop_styleref(self, rec, cfg): pass

    # Shadow tags
#    def handle_shadowcontroller(self, rec, cfg): pass
#    def handle_shadow(self, rec, cfg): pass

    # Bevel tags
#    def handle_bevel(self, rec, cfg): pass
#    def handle_bevattr_indent(self, rec, cfg): pass
#    def handle_bevattr_lightangle(self, rec, cfg): pass
#    def handle_bevattr_contrast(self, rec, cfg): pass
#    def handle_bevattr_type(self, rec, cfg): pass
#    def handle_bevelink(self, rec, cfg): pass

    # Blend on a curve tags
#    def handle_blender_curveprop(self, rec, cfg): pass
#    def handle_blend_path(self, rec, cfg): pass
#    def handle_blender_curveangles(self, rec, cfg): pass

    # Contouring tags
#    def handle_contourcontroller(self, rec, cfg): pass
#    def handle_contour(self, rec, cfg): pass

    # Set tags
#    def handle_setsentinel(self, rec, cfg): pass
#    def handle_setproperty(self, rec, cfg): pass

    # More Blend on a curve tags
#    def handle_blendprofiles(self, rec, cfg): pass
#    def handle_blenderadditional(self, rec, cfg): pass
#    def handle_nodeblendpath_filled(self, rec, cfg): pass

    # Multi stage fill tags
    def handle_linearfillmultistage(self, rec, cfg):
        trafo = self.get_trafo()
        vector = apply_trafo_to_points([rec.start_point, rec.end_point], trafo)
        start_colour = self.get_color(rec.start_colour)
        end_colour = self.get_color(rec.end_colour)

        stops = [[0.0, start_colour]]
        for p in rec.stop_colors:
            stops.append([p[0], self.get_color(p[1])])
        stops.append([1.0, end_colour])

        self.style['gradient_fill'] = [
            sk2const.GRADIENT_LINEAR,
            vector,
            stops,
            sk2const.GRADIENT_EXTEND_PAD
        ]

    def handle_circularfillmultistage(self, rec, cfg):
        trafo = self.get_trafo()
        points = [rec.centre_point, rec.edge_point]
        vector = apply_trafo_to_points(points, trafo)
        start_colour = self.get_color(rec.start_colour)
        end_colour = self.get_color(rec.end_colour)

        stops = [[0.0, start_colour]]
        for p in rec.stop_colors:
            stops.append([p[0], self.get_color(p[1])])
        stops.append([1.0, end_colour])

        self.style['gradient_fill'] = [
            sk2const.GRADIENT_RADIAL,
            vector,
            stops,
            sk2const.GRADIENT_EXTEND_PAD
        ]

    def handle_ellipticalfillmultistage(self, rec, cfg):
        trafo = self.get_trafo()
        start_colour = self.get_color(rec.start_colour)
        end_colour = self.get_color(rec.end_colour)

        stops = [[0.0, start_colour]]
        for p in rec.stop_colors:
            stops.append([p[0], self.get_color(p[1])])
        stops.append([1.0, end_colour])

        self.style['gradient_fill'] = [
            sk2const.GRADIENT_RADIAL,
            [[0.0, 0.0], [1.0, 0.0]],
            stops,
            sk2const.GRADIENT_EXTEND_PAD  # TODO
        ]

        # print self.sk2_doc.doc_file
        tr = make_trafo(rec.centre_point, rec.major_axes, rec.minor_axes, trafo)
        self.style['fill_trafo'] = tr

    #    def handle_conicalfillmultistage(self, rec, cfg): pass

    # Brush attribute tags
#    def handle_brushattr(self, rec, cfg): pass
#    def handle_brushdefinition(self, rec, cfg): pass
#    def handle_brushdata(self, rec, cfg): pass
#    def handle_morebrushdata(self, rec, cfg): pass
#    def handle_morebrushattr(self, rec, cfg): pass

    # ClipView tags
#    def handle_clipviewcontroller(self, rec, cfg): pass
#    def handle_clipview(self, rec, cfg): pass

    # Feathering tags
#    def handle_feather(self, rec, cfg): pass

    # Bar properties tag
#    def handle_barproperty(self, rec, cfg): pass

    # Other multi stage fill tags
#    def handle_squarefillmultistage(self, rec, cfg): pass

    # More brush tags
#    def handle_evenmorebrushdata(self, rec, cfg): pass
#    def handle_evenmorebrushattr(self, rec, cfg): pass
#    def handle_timestampbrushdata(self, rec, cfg): pass
#    def handle_brushpressureinfo(self, rec, cfg): pass
#    def handle_brushpressuredata(self, rec, cfg): pass
#    def handle_brushattrpressureinfo(self, rec, cfg): pass
#    def handle_brushcolourdata(self, rec, cfg): pass
#    def handle_brushpressuresampledata(self, rec, cfg): pass
#    def handle_brushtimesampledata(self, rec, cfg): pass
#    def handle_brushattrfillflags(self, rec, cfg): pass
#    def handle_brushtranspinfo(self, rec, cfg): pass
#    def handle_brushattrtranspinfo(self, rec, cfg): pass

    # Nudge size record
#    def handle_documentnudge(self, rec, cfg): pass

    # Bitmap properties record
#    def handle_bitmap_properties(self, rec, cfg): pass

    # Bitmap smoothing record
#    def handle_documentbitmapsmoothing(self, rec, cfg): pass

    # XPE bitmap processing record
#    def handle_xpe_bitmap_properties(self, rec, cfg): pass

    # XPE Bitmap file format placeholder record
#    def handle_definebitmap_xpe(self, rec, cfg): pass

    # Current attributes records
#    def handle_currentattributes(self, rec, cfg): pass
#    def handle_currentattributebounds(self, rec, cfg): pass

    # 3-point linear fill records
#    def handle_linearfill3POINT = 4121
#    def handle_linearfillmultistage3POINT = 4122
#    def handle_lineartransparentfill3POINT = 4123

    # Duplication distance record
#    def handle_duplicationoffset(self, rec, cfg): pass

    # Bitmap effect tags
#    def handle_live_effect(self, rec, cfg): pass
#    def handle_locked_effect(self, rec, cfg): pass
#    def handle_feather_effect(self, rec, cfg): pass

    # Miscellaneous records
#    def handle_compoundrender(self, rec, cfg): pass
#    def handle_objectbounds(self, rec, cfg): pass

    def handle_spread_phase2(self, rec, cfg):
        self.handle_spread(rec, cfg)

#    def handle_currentattributes_phase2 = 4132
#    def handle_spread_flashprops(self, rec, cfg): pass
#    def handle_printersettings_phase2 = 4135
#    def handle_documentinformation(self, rec, cfg): pass
#    def handle_clipview_path(self, rec, cfg): pass

    def handle_definebitmap_png_real(self, rec, cfg):
        self.bitmaps[rec.idx] = rec.bitmap_data

#    def handle_text_string_pos(self, rec, cfg): pass
#    def handle_spread_flashprops2(self, rec, cfg): pass
#    def handle_text_linespace_leading(self, rec, cfg): pass

    # New text records
#    def handle_text_tab(self, rec, cfg): pass
#    def handle_text_left_indent(self, rec, cfg): pass
#    def handle_text_first_indent(self, rec, cfg): pass
#    def handle_text_right_indent(self, rec, cfg): pass
#    def handle_text_ruler(self, rec, cfg): pass
#    def handle_text_story_height_info(self, rec, cfg): pass
#    def handle_text_story_link_info(self, rec, cfg): pass
#    def handle_text_story_translation_info(self, rec, cfg): pass
#    def handle_text_space_before(self, rec, cfg): pass
#    def handle_text_space_after(self, rec, cfg): pass
#    def handle_text_special_hyphen(self, rec, cfg): pass
#    def handle_text_soft_return(self, rec, cfg): pass
#    def handle_text_extra_font_info(self, rec, cfg): pass
#    def handle_text_extra_tt_font_def(self, rec, cfg): pass
#    def handle_text_extra_atm_font_def(self, rec, cfg): pass

#    # def handle_units(self):
#    #     self.sk2_mtds.set_doc_units(uc2const.UNIT_PT)

    def get_color(self, colour_ref):
        return self.colors.get(colour_ref) or xar_const.RGB_BLACK

    def set_trafo(self, trafo):
        self.trafo = trafo

    def get_trafo(self):
        return copy.deepcopy(self.trafo)

    def get_text_style(self):
        fill = self.get_fill()
        stroke = self.get_stoke()
        font_family = self.style['text_font_family']
        font_face = self.style['text_bold'] and 'Bold' or ''
        font_face += self.style['text_italic'] and 'Italic' or ''
        font_face = font_face or 'Regular'
        font_size = self.style['text_script_size'] or 1.0
        alignment = XAR_TO_SK2_TEXT_ALIGN.get(
            self.style['text_justification'],
            sk2const.TEXT_ALIGN_LEFT
        )
        image_style = []
        text_style = [font_family, font_face, font_size, alignment, [], True]
        return [fill, stroke, text_style, image_style]

    def get_style(self, stroke=False, fill=False):
        fill = fill and self.get_fill() or []
        stroke = stroke and self.get_stoke() or []
        return [fill, stroke, [], []]

    def get_fill_trafo(self):
        return self.style.get('fill_trafo') or []

    def get_fill(self):
        fill_rule = XAR_TO_SK2_WINDING.get(
            self.style['winding_rule'],
            sk2const.FILL_EVENODD
        )
        fill_data = []
        fill_type = sk2const.FILL_SOLID
        if self.style.get('pattern_fill'):
            fill_type = sk2const.FILL_PATTERN
            fill_data = copy.deepcopy(self.style['pattern_fill'])

        elif self.style.get('gradient_fill'):
            fill_type = sk2const.FILL_GRADIENT
            fill_data = copy.deepcopy(self.style['gradient_fill'])
            fill_repeating = self.style.get('fill_repeating')
            fill_effect = self.style['fill_effect']

            fill_data = self.apply_fill_effect(fill_data, fill_effect)
            fill_data = self.apply_fill_repeating(fill_data, fill_repeating)

            fill_data[3] = XAR_TO_SK2_FILL_REPEATING.get(fill_repeating)
            fill_data[3] = fill_data[3] or sk2const.GRADIENT_EXTEND_PAD

        elif self.style.get('flat_colour_fill'):
            fill_type = sk2const.FILL_SOLID
            fill_data = copy.deepcopy(self.style['flat_colour_fill'])

        if fill_data:
            return [fill_rule, fill_type, fill_data]
        return []

    def get_stoke(self):
        colour = self.style['stroke_colour']
        if colour is None:
            return []
        cap_style = XAR_TO_SK2_CAP.get(
            self.style['start_cap'], sk2const.CAP_BUTT
        )
        join_style = XAR_TO_SK2_JOIN.get(
            self.style['join_type'], sk2const.JOIN_MITER
        )
        rule = sk2const.STROKE_MIDDLE
        width = self.style['line_width']
        colour = copy.deepcopy(self.style['stroke_colour'])
        dash = []  # TODO
        miter_limit = self.style['mitre_limit'] / 1000.0
        behind_flag = 0  # TODO
        scalable_flag = 0  # TODO
        markers = [[], []]  # TODO
        return [rule, width, colour, dash, cap_style, join_style, miter_limit,
                behind_flag, scalable_flag, markers]

    def get_path(self, rec):
        paths = []
        for closed, points in self.xar_mtds.read_path(zip(rec.verb, rec.coord)):
            marker = sk2const.CURVE_CLOSED if closed else sk2const.CURVE_OPENED
            path = []
            for point in points:
                if len(point) == 3:
                    point = [point[0], point[1], point[2], sk2const.NODE_CUSP]
                path.append(point)
            paths.append([path[0], path[1:], marker])
        return paths

    def get_path_relative(self, rec):
        paths = []
        for closed, points in self.xar_mtds.read_path_relative(rec.path):
            marker = sk2const.CURVE_CLOSED if closed else sk2const.CURVE_OPENED
            path = []
            for point in points:
                if len(point) == 3:
                    point = [point[0], point[1], point[2], sk2const.NODE_CUSP]
                path.append(point)
            paths.append([path[0], path[1:], marker])
        return paths

    def apply_fill_effect(self, fill_data, fill_effect):
        """
        TAG_FILLEFFECT_FADE: Transform the start colour into the end colour
        by taking the shortest route between the 2 colours, in RGB colour space.
        TAG_FILLEFFECT_RAINBOW: Transform the start colour into the end colour
        by taking the shortest route in the H dimension of the HSV colour space.
        TAG_FILLEFFECT_ALTRAINBOW: Transform the start colour into the end
        colour by taking the longest route in the H dimension of the HSV
        colour space.
        """
        if fill_effect in RAINBOW_EFFECT:
            if fill_effect == xar_const.TAG_FILLEFFECT_RAINBOW:
                shortest_route = True
            elif fill_effect == xar_const.TAG_FILLEFFECT_ALTRAINBOW:
                shortest_route = False
            stops = fill_data[2]
            new_stops = []
            for piece in range(0, len(stops)-1):
                start = stops[piece]
                end = stops[piece+1]
                new_stops.append(start)
                new_stops.extend(
                    self.get_rainbow_piece(start, end, shortest_route)
                )
            new_stops.append(end)
            fill_data[2] = new_stops

        return fill_data

    def flush_stack(self, parent):
        for el in self.stack:
            el.parent = parent
        parent.childs.extend(self.stack)
        self.stack = []

    def apply_fill_repeating(self, fill_data, fill_repeating):
        if fill_repeating == xar_const.TAG_FILL_REPEATING_EXTRA:
            """ TAG_FILL_REPEATING_EXTRA: The fill is repeated with the start 
            point being the start colour and a point half-way through the fill 
            being the end colour. The fill then fades back to the start colour 
            at the end point and then repeats indefinitely. This can apply to 
            linear, circular, elliptical and diamond fills.
            """
            stops = fill_data[2]
            s1 = [[a[0] / 2.0, a[1]] for a in stops[:-1]]
            s2 = [[1.0 - a[0] / 2.0, a[1]] for a in reversed(stops)]
            fill_data[2] = s1 + s2
        return fill_data

    def get_rainbow_piece(self, start_colour, end_colour, shortest_route=True):
        # TODO: implement this
        rainbow_piece = []
        return rainbow_piece


class SK2_to_XAR_Translator(object):
    xar_doc = None
    xar_model = None
    xar_mtds = None
    # page = None
    # fontmap = None

    def translate(self, sk2_doc, xar_doc):
        self.xar_doc = xar_doc
        self.xar_model = xar_doc.model
        self.xar_mtds = xar_doc.methods
        rec = self._TAG_FILEHEADER(sk2_doc)
        self.xar_model.add(rec)
        self.process_element(sk2_doc.model)
        rec = self._TAG_ENDOFFILE(sk2_doc)
        self.xar_model.add(rec)

    def process_element(self, element):
        for child in element.childs:
            self.process_element(child)

    def _TAG_FILEHEADER(self, sk2_doc):
        rec = xar_model.XARRecord(xar_const.TAG_FILEHEADER, 0)
        rec.file_size = 0
        rec.file_type = xar_const.FILE_TYPE_PAPER_PUBLISH
        rec.producer = sk2_doc.appdata.app_name
        rec.producer_version = sk2_doc.appdata.version
        rec.producer_build = sk2_doc.appdata.revision
        return rec

    def _TAG_ENDOFFILE(self, sk2_doc):
        return xar_model.XARRecord(xar_const.TAG_ENDOFFILE, 1)
