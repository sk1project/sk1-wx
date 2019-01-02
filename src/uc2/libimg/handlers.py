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
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import os
from base64 import b64decode, b64encode
from cStringIO import StringIO
from copy import deepcopy

from PIL import Image, ImageOps

from uc2 import uc2const
from uc2.cms import val_255
from uc2.libcairo import image_to_surface
from uc2.utils import fsutils
from . import magickwand

TIFF_FMT = 'TIFF'
PNG_FMT = 'PNG'

LOG = logging.getLogger(__name__)


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

    def get_mode(self):
        return self.bitmap.mode if self.bitmap else None

    def has_alpha(self):
        return self.alpha is not None

    def clear_cache(self):
        self.cdata = None
        self.ps_cdata = None
        self.gray_cdata = None

    def _get_saver_fmt(self, image):
        return TIFF_FMT if image.mode == uc2const.IMAGE_CMYK else PNG_FMT

    def _image2str(self, image):
        if not image:
            return None
        fobj = StringIO()
        image.save(fobj, format=self._get_saver_fmt(image))
        return fobj.getvalue()

    def _str2image(self, image_str=None):
        if not image_str:
            return None
        image = Image.open(StringIO(image_str))
        image.load()
        return image

    def get_bitmap_b64str(self):
        bitmap_str = self._image2str(self.bitmap)
        return b64encode(bitmap_str) if bitmap_str else None

    def get_alpha_b64str(self):
        alpha_str = self._image2str(self.alpha)
        return b64encode(alpha_str) if alpha_str else None

    def set_images(self, bitmap=None, alpha=None):
        self.bitmap = bitmap if bitmap else self.bitmap
        self.alpha = alpha if alpha else self.alpha
        self.clear_cache()

    def set_images_from_str(self, bitmap_str=None, alpha_str=None):
        self.set_images(self._str2image(bitmap_str),
                        self._str2image(alpha_str))

    def set_images_from_b64str(self, bitmap_str=None, alpha_str=None):
        bitmap_str = b64decode(bitmap_str) if bitmap_str else None
        alpha_str = b64decode(alpha_str) if alpha_str else None
        self.set_images_from_str(bitmap_str, alpha_str)

    # Pixmap loading
    def update_cache(self, cms):
        pass

    def load_from_images(self, cms, image, alpha=None):
        image.load()
        LOG.debug('Image mode %s', image.mode)
        if alpha:
            alpha.load()

        profile = image.info.get('icc_profile', None)

        if image.mode == 'P' and 'transparency' in image.info:
            image = image.convert(uc2const.IMAGE_RGBA)
        LOG.debug('Image mode %s', image.mode)

        if not alpha and image.mode.endswith('A'):
            alpha = image.split()[-1]
        if image.mode == uc2const.IMAGE_GRAY_A:
            image = image.convert(uc2const.IMAGE_GRAY)

        if image.mode not in uc2const.SUPPORTED_CS:
            if image.mode != uc2const.IMAGE_RGBA:
                profile = None
            image = image.convert(uc2const.IMAGE_RGB)
        LOG.debug('Image mode %s', image.mode)

        if image.mode not in uc2const.SUPPORTED_CS[1:]:
            profile = None

        if profile:
            try:
                image = cms.adjust_image(image, profile)
            except Exception as e:
                LOG.warning('Error adjusting image: %s', e)

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
        self.update_cache(cms)

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
            LOG.debug('Try loading by PIL')
            self._load_by_pil(cms, fileptr)
        except IOError:
            LOG.debug('PIL cannot load this image. Try loading by ImageMagick')
            self._load_by_magickwand(cms, fileptr)

    def load_from_file(self, cms, filepath):
        self.load_from_fileptr(cms, fsutils.get_fileptr(filepath))

    def load_from_b64str(self, cms, b64str):
        self.load_from_fileptr(cms, StringIO(b64decode(b64str)))

    def extract_bitmap(self, filepath):
        ext = '.tiff' if self.bitmap.mode == uc2const.IMAGE_CMYK else '.png'
        path, file_ext = os.path.splitext(filepath)
        filepath = path + ext if not file_ext == ext else filepath
        fileptr = fsutils.get_fileptr(filepath, True)
        self.bitmap.save(fileptr, format=self._get_saver_fmt(self.bitmap))
        fileptr.close()
        if self.alpha:
            fileptr = fsutils.get_fileptr(path + '_alphachannel.png', True)
            self.bitmap.save(fileptr, format=PNG_FMT)
            fileptr.close()


class DrawableImageHandler(ImageHandler):
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

    def get_display_image(self, cms, proofing=False):
        image = self.bitmap
        if image.mode in uc2const.DUOTONES:
            if image.mode == uc2const.IMAGE_MONO:
                image = image.convert(uc2const.IMAGE_GRAY)
            size = image.size
            fg = self.pixmap.style[3][0]
            bg = self.pixmap.style[3][1]
            if proofing:
                fg = cms.get_cmyk_color(fg) if fg else None
                bg = cms.get_cmyk_color(bg) if bg else None
            fg = tuple(cms.get_display_color255(fg)) if fg else None
            bg = tuple(cms.get_display_color255(bg)) if bg else None

            display_image = fg_img = bg_img = None
            if fg:
                fg_img = Image.new(uc2const.IMAGE_RGB, size, fg)
            if bg:
                bg_img = Image.new(uc2const.IMAGE_RGB, size, bg)
            if fg_img and bg_img:
                bg_img.paste(fg_img, (0, 0), ImageOps.invert(image))
                display_image = bg_img
            elif fg_img:
                display_image = fg_img
                if self.alpha:
                    alpha = self.alpha.copy()
                    alpha.paste(ImageOps.invert(image), (0, 0), image)
                else:
                    alpha = ImageOps.invert(image)
                display_image.putalpha(alpha)
            elif bg_img:
                display_image = bg_img
                if self.alpha:
                    alpha = self.alpha.copy()
                    alpha.paste(image, (0, 0), ImageOps.invert(image))
                else:
                    alpha = image.copy()
                display_image.putalpha(alpha)
            return display_image
        if proofing and image.mode != uc2const.IMAGE_CMYK:
            image = cms.convert_image(image, uc2const.IMAGE_CMYK)
        return cms.get_display_image(image)

    def _get_surface(self, cms, proofing=False, stroke_mode=False):
        if stroke_mode:
            gray_image = self.bitmap.convert(uc2const.IMAGE_GRAY)
            rgb_image = gray_image.convert(uc2const.IMAGE_RGB)
        else:
            rgb_image = self.get_display_image(cms, proofing)

        if rgb_image is None:
            return None

        if self.alpha and rgb_image.mode == uc2const.IMAGE_RGB:
            rgb_image.putalpha(self.alpha)

        return image_to_surface(rgb_image)

    def get_surface(self, cms, proofing=False, stroke_mode=False):
        if stroke_mode:
            if not self.gray_cdata:
                self.gray_cdata = self._get_surface(cms, stroke_mode=True)
            return self.gray_cdata
        elif proofing:
            if not self.ps_cdata:
                self.ps_cdata = self._get_surface(cms, proofing=True)
            return self.ps_cdata
        else:
            if not self.cdata:
                self.cdata = self._get_surface(cms)
            return self.cdata

    def update_cache(self, cms):
        self.get_surface(cms, cms.proofing)


class EditableImageHandler(DrawableImageHandler):

    def copy(self, pixmap=None):
        pixmap = pixmap or self.pixmap
        hdl = EditableImageHandler(pixmap)
        hdl.set_images(self.bitmap.copy() if self.bitmap else None,
                       self.alpha.copy() if self.alpha else None)
        return hdl

    def remove_alpha(self):
        self.alpha = None
        self.clear_cache()

    def invert_alpha(self):
        if self.alpha:
            self.alpha = ImageOps.invert(self.alpha)
            self.clear_cache()

    def invert_image(self, cms):
        if self.bitmap.mode == uc2const.IMAGE_MONO:
            image = ImageOps.invert(self.bitmap.convert(uc2const.IMAGE_GRAY))
            bitmap = image.convert(uc2const.IMAGE_MONO)
        elif self.bitmap.mode == uc2const.IMAGE_CMYK:
            image = cms.convert_image(self.bitmap, uc2const.IMAGE_RGB)
            inv_image = ImageOps.invert(image)
            bitmap = cms.convert_image(inv_image, uc2const.IMAGE_CMYK)
        elif self.bitmap.mode == uc2const.IMAGE_LAB:
            image = cms.convert_image(self.bitmap, uc2const.IMAGE_RGB)
            inv_image = ImageOps.invert(image)
            bitmap = cms.convert_image(inv_image, uc2const.IMAGE_LAB)
        else:
            bitmap = ImageOps.invert(self.bitmap)
        self.set_images(bitmap)

    def convert_image(self, cms, colorspace):
        if self.bitmap.mode in uc2const.DUOTONES:
            if colorspace not in uc2const.DUOTONES:
                bitmap = self.get_display_image(cms)
                alpha = None
                if self.alpha and bitmap.mode == uc2const.IMAGE_RGB:
                    alpha = self.alpha
                elif bitmap.mode == uc2const.IMAGE_RGBA:
                    alpha = bitmap.split()[-1]
                    bitmap = bitmap.convert(uc2const.IMAGE_RGB)
                if colorspace != uc2const.IMAGE_RGB:
                    bitmap = cms.convert_image(bitmap, colorspace)
                self.set_images(bitmap, alpha)
            else:
                bitmap = self.bitmap.convert(colorspace)
                self.set_images(bitmap)
        else:
            if colorspace == uc2const.IMAGE_MONO:
                bitmap = cms.convert_image(self.bitmap, uc2const.IMAGE_GRAY)
                bitmap = bitmap.convert(colorspace)
                self.set_images(bitmap)
            else:
                bitmap = cms.convert_image(self.bitmap, colorspace)
                self.set_images(bitmap)

    def _transpose(self, method=None):
        if method is not None:
            bitmap = self.bitmap.transpose(method)
            alpha = self.alpha.transpose(method) if self.alpha else None
            self.set_images(bitmap, alpha)

    def flip_top_to_bottom(self):
        self._transpose(Image.FLIP_TOP_BOTTOM)

    def flip_left_to_right(self):
        self._transpose(Image.FLIP_LEFT_RIGHT)
