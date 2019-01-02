# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013-2016 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <https://www.gnu.org/licenses/>.

import cairo
import wx
from PIL import Image, ImageOps

import const


def get_bitmap_size(bitmap):
    return bitmap.GetSize()


def stream_to_image(image_stream):
    image_stream.seek(0)
    return wx.ImageFromStream(image_stream)


def stream_to_bitmap(image_stream):
    return stream_to_image(image_stream).ConvertToBitmap()


# ----- PIL interfaces

def image_to_pil_image(image):
    """
    Converts wx.Image to PIL Image object.
    """
    pil_image = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
    pil_image.frombytes(image.GetData())
    if image.HasAlpha():
        alpha = Image.new('L', (image.GetWidth(), image.GetHeight()))
        alpha.frombytes(image.GetAlphaData())
        pil_image.putalpha(alpha)
    return pil_image


def pil_image_to_image(pil_image):
    """
    Converts PIL Image object to wx.Image.
    """
    image = wx.EmptyImage(*pil_image.size)
    if pil_image.mode[-1] == 'A':
        image.SetData(pil_image.convert('RGB').tobytes())
        image.SetAlphaData(pil_image.tobytes()[3::4])
    else:
        image.SetData(pil_image.tobytes())
    return image


def bitmap_to_pil_image(bitmap):
    """
    Converts wx.Bitmap to PIL Image object.
    """
    return image_to_pil_image(bitmap.ConvertToImage())


def pil_image_to_bitmap(pil_image):
    """
    Converts PIL Image object to wx.Bitmap.
    """
    return pil_image_to_image(pil_image).ConvertToBitmap()


# ----- Cairo interfaces

def copy_surface_to_bitmap(surface):
    """
    Create a wx.Bitmap from a Cairo ImageSurface.
    """
    cairo_format = surface.get_format()
    if cairo_format not in [cairo.FORMAT_ARGB32, cairo.FORMAT_RGB24]:
        raise TypeError("Unsupported format")

    width = surface.get_width()
    height = surface.get_height()
    stride = surface.get_stride()
    data = surface.get_data()
    if cairo_format == cairo.FORMAT_ARGB32:
        fmt = wx.BitmapBufferFormat_ARGB32
        bmp = wx.EmptyBitmapRGBA(width, height)
    else:
        fmt = wx.BitmapBufferFormat_RGB32
        bmp = wx.EmptyBitmap(width, height, 32)
    bmp.CopyFromBuffer(data, fmt, stride)
    return bmp


def copy_bitmap_to_surface(bitmap):
    """
    Create an ImageSurface from a wx.Bitmap
    """
    width, height = bitmap.GetSize()
    if bitmap.HasAlpha():
        cairo_format = cairo.FORMAT_ARGB32
        fmt = wx.BitmapBufferFormat_ARGB32
    else:
        cairo_format = cairo.FORMAT_RGB24
        fmt = wx.BitmapBufferFormat_RGB32

    try:
        stride = cairo.ImageSurface.format_stride_for_width(cairo_format, width)
    except AttributeError:
        stride = width * 4

    surface = cairo.ImageSurface(cairo_format, width, height)
    bitmap.CopyToBuffer(surface.get_data(), fmt, stride)
    return surface


# ----- Text routines

def get_text_size(text, bold=False, size_incr=0):
    font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
    if bold:
        font.SetWeight(wx.FONTWEIGHT_BOLD)
    if size_incr:
        if font.IsUsingSizeInPixels():
            sz = font.GetPixelSize()[1] + size_incr
            font.SetPixelSize((0, sz))
        else:
            sz = font.GetPointSize() + size_incr
            font.SetPointSize(sz)
    pdc = wx.MemoryDC()
    bmp = wx.EmptyBitmap(1, 1)
    pdc.SelectObject(bmp)
    pdc.SetFont(font)
    height = pdc.GetCharHeight()
    width = pdc.GetTextExtent(text)[0]
    result = (width, height)
    pdc.SelectObject(wx.NullBitmap)
    return result


def invert_text_bitmap(bmp, color=(0, 0, 0)):
    w, h = bmp.GetSize()
    img = bmp.ConvertToImage()
    img.ConvertColourToAlpha(0, 0, 0)
    img.SetRGBRect(wx.Rect(0, 0, w, h), *color)
    return img.ConvertToBitmap()


def text_to_bitmap(text, bold=False):
    w, h = get_text_size(text, bold)
    dc = wx.MemoryDC()
    bmp = wx.EmptyBitmap(w, h)
    dc.SelectObject(bmp)
    dc.SetBackground(wx.Brush("white"))
    dc.Clear()
    font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
    if bold:
        font.SetWeight(wx.FONTWEIGHT_BOLD)
    dc.SetFont(font)
    dc.SetTextForeground(wx.Colour(*const.UI_COLORS['text']))
    dc.DrawText(text, 0, 0)
    image = bitmap_to_pil_image(bmp)
    image.putalpha(ImageOps.invert(image).convert('L'))
    ret = pil_image_to_bitmap(image)
    dc.EndDrawing()
    dc.SelectObject(wx.NullBitmap)
    return ret, (w, h)


def bmp_to_white(bmp):
    image = bmp.ConvertToImage()
    w, h = bmp.GetSize()
    image.SetRGBRect(wx.Rect(0, 0, w, h), 255, 255, 255)
    return image.ConvertToBitmap()


def disabled_bmp(bmp):
    image = bmp.ConvertToImage()
    image = image.ConvertToGreyscale()
    image = image.AdjustChannels(1.0, 1.0, 1.0, 0.5)
    return image.ConvertToBitmap()


def get_dc(widget):
    pdc = wx.PaintDC(widget)
    try:
        dc = wx.GCDC(pdc)
    except Exception:
        dc = pdc
    pdc.BeginDrawing()
    dc.BeginDrawing()
    return dc


def get_buffered_dc(widget):
    pdc = wx.BufferedPaintDC(widget)
    pdc.BeginDrawing()
    return pdc


class LabelRenderer:
    art_id = None
    art_size = ()
    bmp = None
    disabled_bmp = None
    text = ''
    font = None
    textplace = const.RIGHT

    widget = None
    size = ()
    minsize = ()
    dc = None
    pdc = None

    decoration_padding = 0
    padding = 0
    active_border = 3

    def __init__(
            self, widget, art_id=None, art_size=const.DEF_SIZE, text='',
            padding=0, fontbold=False, fontsize=0, textplace=const.RIGHT):
        self.widget = widget
        self.decoration_padding = widget.decoration_padding
        if art_id:
            self._set_bmp(art_id, art_size)
        self.padding = padding
        self.textplace = textplace
        if not art_id and not text:
            text = 'LABEL'
        if text:
            self.text = text
            self._set_font(fontbold, fontsize)
        self._set_minsize()
        self._adjust_widget_size()

    def _set_bmp(self, art_id, art_size):
        self.bmp = wx.ArtProvider.GetBitmap(art_id, size=art_size)

    def _set_disabled_bmp(self):
        if self.bmp:
            image = self.bmp.ConvertToImage()
            image = image.AdjustChannels(1.0, 1.0, 1.0, .5)
            gray_image = image.ConvertToGreyscale()
            self.disabled_bmp = gray_image.ConvertToBitmap()

    def _set_font(self, bold=False, size=0):
        self.font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        if bold:
            self.font.SetWeight(wx.FONTWEIGHT_BOLD)
        if size:
            if self.font.IsUsingSizeInPixels():
                sz = self.font.GetPixelSize() + size
                self.font.SetPixelSize(sz)
            else:
                sz = self.font.GetPointSize() + size
                self.font.SetPointSize(sz)

    def _set_minsize(self):
        bmp_size = (0, 0)
        text_size = (0, 0)
        border = self.decoration_padding + self.padding
        if self.bmp:
            bmp_size = self.bmp.GetSize()
        if self.text:
            text_size = self._get_text_size(self.text)
        if self.textplace in [const.RIGHT, const.LEFT]:
            h = max(bmp_size[1], text_size[1])
            w = bmp_size[0] + text_size[0]
        else:
            w = max(bmp_size[0], text_size[0])
            h = bmp_size[1] + text_size[1]
        self.minsize = (w + 2 * border, h + 2 * border)

    def _get_text_size(self, text):
        result = (0, 0)
        if self.text:
            if not self.pdc:
                pdc = wx.MemoryDC()
            else:
                pdc = self.pdc
            pdc.SetFont(self.font)
            height = pdc.GetCharHeight()
            if self.textplace in [const.RIGHT, const.LEFT]:
                text += ' '
            width = pdc.GetTextExtent(text)[0]
            result = (width, height)
        return result

    def _adjust_widget_size(self):
        size = self.widget.GetSize()
        self.widget._set_size(
            max(size[0], self.minsize[0]),
            max(size[1], self.minsize[1]))

    # ----- RENDERING
    def _start(self):
        self.size = self.widget.GetSize()
        if not self.size[0] or not self.size[1]:
            self.pdc = wx.PaintDC(self.widget)
        elif const.IS_MSW and self.widget.IsDoubleBuffered():
            self.widget.buffer = wx.EmptyBitmapRGBA(*self.size)
            self.pdc = wx.BufferedPaintDC(self.widget, self.widget.buffer)
        else:
            self.pdc = wx.PaintDC(self.widget)
        try:
            self.dc = wx.GCDC(self.pdc)
        except Exception:
            self.dc = self.pdc
        self.dc.BeginDrawing()

    def _stop(self):
        if not self.pdc == self.dc:
            self.dc.EndDrawing()
            self.pdc.EndDrawing()
        else:
            self.dc.EndDrawing()
        self.pdc = self.dc = None

    def _draw_text(self, text, x, y):
        if self.text:
            self.pdc.SetFont(self.font)
            if self.widget.enabled:
                color = const.UI_COLORS['text']
                self.pdc.SetTextForeground(wx.Colour(*color))
                self.pdc.DrawText(text, x, y)
            else:
                color = const.UI_COLORS['disabled_text_shadow']
                self.pdc.SetTextForeground(wx.Colour(*color))
                self.pdc.DrawText(text, x + 1, y + 1)
                color = const.UI_COLORS['disabled_text']
                self.pdc.SetTextForeground(wx.Colour(*color))
                self.pdc.DrawText(text, x, y)

    def _draw_bmp(self, x, y):
        if self.bmp:
            if self.widget.enabled:
                self.dc.DrawBitmap(self.bmp, x, y, True)
            else:
                if not self.disabled_bmp:
                    self._set_disabled_bmp()
                self.dc.DrawBitmap(self.disabled_bmp, x, y, True)

    def _draw_content(self, shift_x=0, shift_y=0):
        w, h = self.size
        w_min, h_min = self.minsize
        dx = (w - w_min) / 2
        dy = (h - h_min) / 2
        border = self.decoration_padding + self.padding
        shift_x += border + dx
        shift_y += border + dy
        bmp_size = (0, 0)
        text_size = (0, 0)
        if self.bmp:
            bmp_size = self.bmp.GetSize()
        if self.text:
            text_size = self._get_text_size(self.text)
        if self.textplace == const.TOP:
            bmp_hshift = 0
            if bmp_size[0] < w_min:
                bmp_hshift = (w_min - 2 * border - bmp_size[0]) / 2
            add_y = text_size[1] + 2
            self._draw_bmp(shift_x + bmp_hshift, shift_y + add_y)
            text_hshift = 0
            if text_size[0] < w_min:
                text_hshift = (w_min - 2 * border - text_size[0]) / 2
            self._draw_text(self.text, shift_x + text_hshift, shift_y)

        elif self.textplace == const.LEFT:
            bmp_vshift = 0
            if bmp_size[1] < h_min:
                bmp_vshift = (h_min - 2 * border - bmp_size[1]) / 2
            self._draw_bmp(shift_x + text_size[0], shift_y + bmp_vshift)
            text_vshift = 0
            if text_size[1] < h_min:
                text_vshift = (h_min - 2 * border - text_size[1]) / 2
            txt = self.text + ' '
            self._draw_text(txt, shift_x, shift_y + text_vshift)

        elif self.textplace == const.BOTTOM:
            bmp_hshift = 0
            if bmp_size[0] < w_min:
                bmp_hshift = (w_min - 2 * border - bmp_size[0]) / 2
            self._draw_bmp(shift_x + bmp_hshift, shift_y)
            text_hshift = 0
            if text_size[0] < w_min:
                text_hshift = (w_min - 2 * border - text_size[0]) / 2
            add_y = bmp_size[1] + 2
            self._draw_text(self.text, shift_x + text_hshift, shift_y + add_y)

        else:
            bmp_vshift = 0
            if bmp_size[1] < h_min:
                bmp_vshift = (h_min - 2 * border - bmp_size[1]) / 2
            self._draw_bmp(shift_x, shift_y + bmp_vshift)
            text_vshift = 0
            if text_size[1] < h_min:
                text_vshift = (h_min - 2 * border - text_size[1]) / 2
            txt = ' ' + self.text
            self._draw_text(txt, shift_x + bmp_size[0], shift_y + text_vshift)

    # ----- API
    def draw_normal(self):
        self._start()
        self._draw_content()
        self._stop()

    def draw_disabled(self):
        self._start()
        self._draw_content()
        self._stop()


class ButtonRenderer(LabelRenderer):
    def __init__(
            self, widget, art_id=None, art_size=const.DEF_SIZE, text='',
            padding=0, fontbold=False, fontsize=0, textplace=const.RIGHT):

        LabelRenderer.__init__(
            self, widget, art_id, art_size,
            text, padding, fontbold, fontsize, textplace)

    # ----- RENDERING

    def _draw_border(self):
        color = const.UI_COLORS['hover_solid_border']
        self.pdc.SetPen(wx.Pen(wx.Colour(*color), 1))
        self.pdc.SetBrush(wx.TRANSPARENT_BRUSH)
        w, h = self.widget.GetSize()
        self.pdc.DrawRoundedRectangle(0, 0, w, h, 3.0)

    def _draw_normal(self, flat=True):
        if flat:
            return
        self._draw_hover()

    def _draw_disabled(self, flat=True):
        if flat:
            return
        self._draw_border()

    def _draw_hover(self):
        w, h = self.size

        color = const.UI_COLORS['light_shadow']
        self.dc.SetPen(wx.Pen(wx.Colour(*color), 2))
        self.dc.SetBrush(wx.TRANSPARENT_BRUSH)
        self.dc.DrawRoundedRectangle(2, 2, w - 2, h - 2, 3.0)

        color = const.UI_COLORS['dark_shadow']
        self.dc.SetPen(wx.Pen(wx.Colour(*color), self.active_border))
        self.dc.DrawLine(4, h - 2, w - 3, h - 2)
        self.dc.DrawLine(w - 2, 4, w - 2, h - 3)

        color = const.UI_COLORS['hover_solid_border']
        if const.IS_MSW and self.widget.IsDoubleBuffered():
            gc = self.dc.GetGraphicsContext()
            gc.SetAntialiasMode(wx.ANTIALIAS_NONE)
            self.dc.SetPen(wx.Pen(wx.Colour(*color), 1))
            self.dc.SetBrush(wx.TRANSPARENT_BRUSH)
            self.dc.DrawRoundedRectangle(0, 0, w, h, 3.0)
        else:
            self.pdc.SetPen(wx.Pen(wx.Colour(*color), 1))
            self.pdc.SetBrush(wx.TRANSPARENT_BRUSH)
            self.pdc.DrawRoundedRectangle(0, 0, w, h, 3.0)

    def _draw_pressed(self):
        w, h = self.size

        color = const.UI_COLORS['dark_shadow']
        self.dc.SetPen(wx.Pen(wx.Colour(*color), self.active_border))
        self.dc.DrawLine(3, 1, w - 3, 1)
        self.dc.DrawLine(1, 3, 1, h - 3)

        color = const.UI_COLORS['dark_shadow']
        self.dc.SetPen(wx.Pen(wx.Colour(*color), self.active_border))
        self.dc.SetBrush(wx.Brush(wx.Colour(*color)))
        self.dc.DrawRoundedRectangle(2, 2, w - 2, h - 2, 3.0)

        color = const.UI_COLORS['hover_solid_border']
        if const.IS_MSW and self.widget.IsDoubleBuffered():
            gc = self.dc.GetGraphicsContext()
            gc.SetAntialiasMode(wx.ANTIALIAS_NONE)
            self.dc.SetPen(wx.Pen(wx.Colour(*color), 1))
            self.dc.SetBrush(wx.TRANSPARENT_BRUSH)
            self.dc.DrawRoundedRectangle(0, 0, w, h, 3.0)
        else:
            self.pdc.SetPen(wx.Pen(wx.Colour(*color), 1))
            self.pdc.SetBrush(wx.TRANSPARENT_BRUSH)
            self.pdc.DrawRoundedRectangle(0, 0, w, h, 3.0)

    def _draw_pressed_disabled(self):
        self._draw_pressed()

    # ----- API

    def draw_normal(self, flat=True):
        self._start()
        self._draw_normal(flat)
        self._draw_content()
        self._stop()

    def draw_hover(self):
        self._start()
        self._draw_hover()
        self._draw_content()
        self._stop()

    def draw_pressed(self):
        self._start()
        self._draw_pressed()
        self._draw_content(shift_x=1, shift_y=1)
        self._stop()

    def draw_disabled(self, flat=True):
        self._start()
        self._draw_disabled(flat)
        self._draw_content()
        self._stop()

    def draw_pressed_disabled(self):
        self._start()
        self._draw_pressed_disabled()
        self._draw_content(shift_x=1, shift_y=1)
        self._stop()


class NativeButtonRenderer(ButtonRenderer):
    nr = None

    def __init__(
            self, widget, art_id=None, art_size=const.DEF_SIZE, text='',
            padding=0, fontbold=False, fontsize=0, textplace=const.RIGHT):

        LabelRenderer.__init__(
            self, widget, art_id, art_size,
            text, padding, fontbold, fontsize, textplace)

    # ----- RENDERING
    def _start(self):
        self.nr = wx.RendererNative.Get()
        LabelRenderer._start(self)

    def _stop(self):
        self.nr = None
        LabelRenderer._stop(self)

    def _draw_normal(self, flat=True):
        if flat:
            return
        w, h = self.size
        self.nr.DrawPushButton(
            self.widget, self.dc, (0, 0, w, h),
            wx.CONTROL_DIRTY)

    def _draw_disabled(self, flat=True):
        if flat:
            return
        w, h = self.size
        self.nr.DrawPushButton(
            self.widget, self.dc, (0, 0, w, h),
            wx.CONTROL_DIRTY | wx.CONTROL_DISABLED)

    def _draw_hover(self):
        w, h = self.size
        self.nr.DrawPushButton(
            self.widget, self.dc, (0, 0, w, h),
            wx.CONTROL_CURRENT)

    def _draw_pressed(self):
        w, h = self.size
        self.nr.DrawPushButton(
            self.widget, self.dc, (0, 0, w, h),
            wx.CONTROL_PRESSED | wx.CONTROL_SELECTED)

    def _draw_pressed_disabled(self):
        w, h = self.size
        self.nr.DrawPushButton(
            self.widget, self.dc, (0, 0, w, h),
            wx.CONTROL_PRESSED | wx.CONTROL_DISABLED | wx.CONTROL_SELECTED)
