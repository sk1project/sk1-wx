# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Igor E. Novikov
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

from copy import deepcopy
from cStringIO import StringIO
from PIL import Image, ImageOps

from uc2 import uc2const
from uc2.cms import val_255
from uc2.utils import fsutils

from . import magickwand


class ImageHandler(object):
    pixmap = None
    bitmap = None
    alpha = None

    cdata = None
    ps_cdata = None
    gray_cdata = None

    def __init__(self, pixmap):
        self.pixmap = pixmap

    def get_size(self):
        return self.bitmap.size if self.bitmap else (0, 0)

    def clear_cache(self):
        self.cdata = None
        self.ps_cdata = None
        self.gray_cdata = None

    def copy(self, pixmap):
        hdl = ImageHandler(pixmap)
        hdl.set_images(self.bitmap.copy() if self.bitmap else None,
                       self.alpha.copy() if self.alpha else None)

    def _get_saver_fmt(self, image):
        return 'TIFF' if image.mode == uc2const.IMAGE_CMYK else 'PNG'

    def _image2str(self, image):
        fobj = StringIO()
        image.save(fobj, format=self._get_saver_fmt(image))
        return fobj.getvalue()

    def _str2image(self, image_str=None):
        if image_str is None:
            return None
        image = Image.open(StringIO(image_str))
        image.load()
        return image

    def set_images_from_str(self, bitmap_str=None, alpha_str=None):
        self.set_images(self._str2image(bitmap_str),
                        self._str2image(alpha_str))

    def set_images(self, bitmap=None, alpha=None):
        self.bitmap = bitmap if bitmap else self.bitmap
        self.alpha = alpha if alpha else self.alpha

    # Pixmap loading
    def load_from_images(self, cms, image, alpha=None):
        image.load()
        if alpha:
            alpha.load()

        profile = image.info.get('icc_profile', None)

        if image.mode == 'P' and 'transparency' in image.info:
            image = image.convert(uc2const.IMAGE_RGBA)

        if not alpha and image.mode.endswith('A'):
            alpha = image.split()[-1]

        if image.mode not in uc2const.SUPPORTED_CS:
            if image.mode != uc2const.IMAGE_RGBA:
                profile = None
            image = image.convert(uc2const.IMAGE_RGB)

        if image.mode not in uc2const.SUPPORTED_CS[1:]:
            profile = None

        if profile:
            try:
                image = cms.adjust_image(image, profile)
            except Exception:
                pass

        cfg = self.pixmap.config
        style = deepcopy(cfg.default_image_style)
        if image.mode in [uc2const.IMAGE_RGB, uc2const.IMAGE_LAB]:
            style[3] = deepcopy(cfg.default_rgb_image_style)
        self.pixmap.style = style

        if alpha:
            if alpha.mode == 'P':
                alpha = alpha.convert(uc2const.IMAGE_RGBA)
            if alpha.mode.endswith('A'):
                alpha = alpha.split()[-1]
        self.set_images(image, alpha)

    def _load_by_pil(self, cms, fileptr):
        fileptr.seek(0)
        self.load_from_images(cms, Image.open(fileptr))

    def _load_by_magickwand(self, cms, fileptr):
        fileptr.seek(0)
        content = fileptr.read()
        image_stream, alpha_stream = magickwand.process_image(content)
        image = Image.open(image_stream)
        alpha = Image.open(alpha_stream) if alpha_stream else None
        self.load_from_images(cms, image, alpha)

    def load_from_fileptr(self, cms, fileptr):
        try:
            self._load_by_pil(cms, fileptr)
        except IOError:
            self._load_by_magickwand(cms, fileptr)

    def load_from_file(self, cms, filepath):
        self.load_from_fileptr(cms, fsutils.get_fileptr(filepath))

    # Rendering
    def convert_duotone_to_image(self, cms, cs=None):
        fg = self.pixmap.style[3][0]
        bg = self.pixmap.style[3][1]
        raw_image = self.bitmap
        fg_cs = bg_cs = uc2const.IMAGE_RGB

        if self.bitmap.mode == uc2const.IMAGE_MONO:
            raw_image = raw_image.convert(uc2const.IMAGE_GRAY)
        size = raw_image.size

        if cs == uc2const.IMAGE_CMYK:
            fg = tuple(cms.get_cmyk_color255(fg)) if fg else ()
            bg = tuple(cms.get_cmyk_color255(bg)) if bg else ()
            fg_cs = bg_cs = cs
        elif cs == uc2const.IMAGE_RGB:
            fg = tuple(cms.get_rgb_color255(fg)) if fg else ()
            bg = tuple(cms.get_rgb_color255(bg)) if bg else ()
            fg_cs = bg_cs = cs
        else:
            if fg:
                fg_cs = fg[0]
                fg = tuple(val_255(cms.get_color(fg, fg_cs)[1]))
            if bg:
                bg_cs = bg[0]
                bg = tuple(val_255(cms.get_color(bg, bg_cs)[1]))

        fg_img = Image.new(fg_cs, size, fg) if fg else None
        bg_img = Image.new(bg_cs, size, bg) if bg else None

        fg_alpha = ImageOps.invert(raw_image) if fg else None
        bg_alpha = raw_image if bg else None

        if self.alpha and any((fg, bg)):
            alpha_chnl = ImageOps.invert(self.alpha)
            comp_img = Image.new('L', size, 0)
            if fg:
                fg_alpha.paste(comp_img, (0, 0), alpha_chnl)
            if bg:
                bg_alpha.paste(comp_img, (0, 0), alpha_chnl)
        return (fg_img, fg_alpha) if fg else None, \
               (bg_img, bg_alpha) if bg else None
