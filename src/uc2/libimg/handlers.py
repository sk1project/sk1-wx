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

import os
from cStringIO import StringIO
from PIL import Image, ImageOps

from uc2.uc2const import IMAGE_CMYK, IMAGE_RGB, IMAGE_RGBA, IMAGE_LAB
from uc2.uc2const import IMAGE_GRAY, IMAGE_MONO, DUOTONES, SUPPORTED_CS
from uc2 import uc2const
from uc2.utils import fsutils


class ImageHandler(object):
    pixmap = None
    bitmap = None
    alpha = None

    cdata = None
    ps_cdata = None
    gray_cdata = None

    def __init__(self, pixmap):
        self.pixmap = pixmap

    def _get_saver_fmt(self, image):
        return 'TIFF' if image.mode == IMAGE_CMYK else 'PNG'

    def _image2str(self, image):
        fobj = StringIO()
        image.save(fobj, format=self._get_saver_fmt(image))
        return fobj.getvalue()

    def _str2image(self, image_str):
        image = Image.open(StringIO(image_str))
        image.load()
        return image

    def set_images_from_str(self, bitmap_str=None, alpha_str=None):
        self.set_images(self._str2image(bitmap_str),
                        self._str2image(alpha_str))

    def set_images(self, bitmap=None, alpha=None):
        self.bitmap = bitmap
        self.alpha = alpha

    def get_size(self):
        return self.bitmap.size if self.bitmap else (0, 0)

    def clear_cache(self):
        self.cdata = None
        self.ps_cdata = None
        self.gray_cdata = None

    def copy(self, pixmap):
        hdl = ImageHandler(pixmap)
        hdl.set_images(self.bitmap.copy(), self.alpha.copy())

    def _load_by_pil(self, fileptr):
        fileptr.seek(0)
        image = Image.open(fileptr)

    def _load_by_magickwand(self, fileptr):
        fileptr.seek(0)
        content = fileptr.read()

    def load_from_fileptr(self, fileptr):
        try:
            self._load_by_pil(fileptr)
        except IOError:
            self._load_by_magickwand(fileptr)

    def load_from_file(self, filepath):
        self.load_from_fileptr(fsutils.get_fileptr(filepath))
