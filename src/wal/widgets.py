# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2018 by Igor E. Novikov
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

import wx
import wx.combo
from wx import animate

import basic
import const
from basic import HPanel, MouseEvent
from const import DEF_SIZE, tr, untr
from mixins import WidgetMixin, DataWidgetMixin, RangeDataWidgetMixin
from renderer import bmp_to_white, disabled_bmp


class Bitmap(wx.StaticBitmap, WidgetMixin):
    bmp = None
    rcallback = None
    lcallback = None

    def __init__(self, parent, bitmap, on_left_click=None, on_right_click=None):
        self.bmp = bitmap
        wx.StaticBitmap.__init__(self, parent, wx.ID_ANY, bitmap)
        if on_left_click:
            self.lcallback = on_left_click
            self.Bind(wx.EVT_LEFT_UP, self._on_left_click, self)
        if on_right_click:
            self.rcallback = on_right_click
            self.Bind(wx.EVT_RIGHT_UP, self._on_right_click, self)

    def _on_right_click(self, event):
        if self.rcallback:
            self.rcallback(MouseEvent(event))

    def _on_left_click(self, event):
        if self.lcallback:
            self.lcallback(MouseEvent(event))

    def _get_bitmap(self):
        if const.IS_MSW and not self.get_enabled():
            return disabled_bmp(self.bmp)
        return self.bmp

    def set_bitmap(self, bmp):
        self.bmp = bmp
        self.SetBitmap(self._get_bitmap())

    def set_enable(self, value):
        WidgetMixin.set_enable(self, value)
        if const.IS_MSW:
            self.set_bitmap(self.bmp)


class Notebook(wx.Notebook, WidgetMixin):
    childs = []
    callback = None

    def __init__(self, parent, on_change=None):
        self.childs = []
        wx.Notebook.__init__(self, parent, wx.ID_ANY)
        if on_change:
            self.callback = on_change
            self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_change, self)

    def _on_change(self, event):
        self.refresh()
        if self.callback:
            self.callback(self.get_active_index())

    def add_page(self, page, title):
        page.layout()
        self.childs.append(page)
        self.AddPage(page, tr(title))

    def remove_page(self, page):
        index = self.childs.index(page)
        self.childs.remove(page)
        self.RemovePage(index)

    def remove_page_by_index(self, index):
        self.childs.remove(self.childs[index])
        self.RemovePage(index)

    def get_active_index(self):
        return self.GetSelection()

    def get_active_page(self):
        return self.childs[self.get_active_index()]

    def set_active_index(self, index):
        self.SetSelection(index)

    def set_active_page(self, page):
        if page in self.childs:
            self.SetSelection(self.childs.index(page))


class VLine(wx.StaticLine, WidgetMixin):
    def __init__(self, parent):
        wx.StaticLine.__init__(self, parent, style=wx.VERTICAL)


class HLine(wx.StaticLine, WidgetMixin):
    def __init__(self, parent):
        wx.StaticLine.__init__(self, parent, style=wx.HORIZONTAL)


class Label(wx.StaticText, WidgetMixin):
    def __init__(self, parent, text='', fontbold=False, fontsize=0, fg=()):
        wx.StaticText.__init__(self, parent, wx.ID_ANY, tr(text))
        font = self.GetFont()
        if fontbold:
            font.SetWeight(wx.FONTWEIGHT_BOLD)
        if fontsize:
            if isinstance(fontsize, str):
                sz = int(fontsize)
                if font.IsUsingSizeInPixels():
                    font.SetPixelSize((0, sz))
                else:
                    font.SetPointSize(sz)
            else:
                if font.IsUsingSizeInPixels():
                    sz = font.GetPixelSize()[1] + fontsize
                    font.SetPixelSize((0, sz))
                else:
                    sz = font.GetPointSize() + fontsize
                    font.SetPointSize(sz)
        self.SetFont(font)
        if fg:
            self.SetForegroundColour(wx.Colour(*fg))
        self.Wrap(-1)

    def set_text(self, text):
        self.SetLabel(tr(text))

    def wrap(self, width):
        self.Wrap(width)


class HtmlLabel(wx.HyperlinkCtrl, WidgetMixin):
    def __init__(self, parent, text, url=''):
        url = text if not url else url
        wx.HyperlinkCtrl.__init__(self, parent, wx.ID_ANY, tr(text), url)


class Button(wx.Button, WidgetMixin):
    callback = None

    def __init__(self, parent, text, size=DEF_SIZE, onclick=None, tooltip='',
                 default=False, pid=wx.ID_ANY):
        wx.Button.__init__(self, parent, pid, tr(text), size=size)
        if default:
            self.SetDefault()
        if onclick:
            self.callback = onclick
            self.Bind(wx.EVT_BUTTON, self.on_click, self)
        if tooltip:
            self.SetToolTipString(tooltip)

    def set_default(self):
        self.SetDefault()

    def on_click(self, event):
        if self.callback:
            self.callback()


class Checkbox(wx.CheckBox, DataWidgetMixin):
    callback = None

    def __init__(self, parent, text='', value=False, onclick=None, right=False):
        style = wx.ALIGN_RIGHT if right else 0
        wx.CheckBox.__init__(self, parent, wx.ID_ANY, tr(text), style=style)
        self.SetValue(True if value else False)
        if onclick:
            self.callback = onclick
            self.Bind(wx.EVT_CHECKBOX, self.on_click, self)

    def set_value(self, val, action=True):
        self.SetValue(val)
        if action:
            self.on_click()

    def on_click(self, event=None):
        if self.callback:
            self.callback()


class NumCheckbox(Checkbox):
    def set_value(self, val, action=True):
        self.SetValue(True if val else False)
        if action:
            self.on_click()

    def get_value(self):
        return 1 if self.GetValue() else 0


class Radiobutton(wx.RadioButton, DataWidgetMixin):
    callback = None

    def __init__(self, parent, text='', onclick=None, group=False):
        style = wx.RB_GROUP if group else 0
        wx.RadioButton.__init__(self, parent, wx.ID_ANY, tr(text), style=style)
        if onclick:
            self.callback = onclick
            self.Bind(wx.wx.EVT_RADIOBUTTON, self.on_click, self)

    def on_click(self, event):
        if self.callback:
            self.callback()


class Combolist(wx.Choice, WidgetMixin):
    items = []
    callback = None

    def __init__(self, parent, size=DEF_SIZE, width=0,
                 items=None, onchange=None):
        items = items or []
        self.items = [tr(item) for item in items]
        size = self._set_width(size, width)
        wx.Choice.__init__(self, parent, wx.ID_ANY, size, choices=self.items)
        if onchange:
            self.callback = onchange
            self.Bind(wx.EVT_CHOICE, self.on_change, self)

    def on_change(self, event):
        if self.callback:
            self.callback()

    def set_items(self, items):
        self.items = [tr(item) for item in items]
        self.SetItems(self.items)

    def set_selection(self, index):
        if index < self.GetCount():
            self.SetSelection(index)

    def get_selection(self):
        return self.GetSelection()

    def set_active(self, index):
        self.set_selection(index)

    def get_active(self):
        return self.get_selection()

    def get_active_value(self):
        return untr(self.items[self.get_selection()])

    def set_active_value(self, val):
        val = tr(val)
        if val not in self.items:
            self.items.append(val)
            self.SetItems(self.items)
        self.set_active(self.items.index[val])


class BitmapChoice(wx.combo.OwnerDrawnComboBox, WidgetMixin):
    def __init__(self, parent, value=0, bitmaps=None):
        self.bitmaps = bitmaps or []
        choices = self._create_items()
        x, y = self.bitmaps[0].GetSize()
        x += 4
        y += 7 + 3
        wx.combo.OwnerDrawnComboBox.__init__(
            self, parent, wx.ID_ANY,
            wx.EmptyString, wx.DefaultPosition,
            (x, y), choices, wx.CB_READONLY,
            wx.DefaultValidator)
        self.set_active(value)

    def OnDrawItem(self, dc, rect, item, flags):
        if item == wx.NOT_FOUND:
            return
        x, y, w, h = wx.Rect(*rect).Get()
        if flags & wx.combo.ODCB_PAINTING_SELECTED and \
                flags & wx.combo.ODCB_PAINTING_CONTROL:
            dc.SetBrush(wx.Brush(wx.WHITE))
            dc.DrawRectangle(x - 1, y - 1, w + 2, h + 2)
            bitmap = self.bitmaps[item]
        elif flags & wx.combo.ODCB_PAINTING_SELECTED:
            if const.IS_MSW:
                pdc = wx.PaintDC(self)
                pdc.SetPen(wx.TRANSPARENT_PEN)
                pdc.SetBrush(wx.Brush(
                    wx.Colour(*const.UI_COLORS['selected_text_bg'])))
                pdc.DrawRectangle(x, y, w, h)
            else:
                render = wx.RendererNative.Get()
                render.DrawItemSelectionRect(self, dc, rect,
                                             wx.CONTROL_SELECTED)
            bitmap = bmp_to_white(self.bitmaps[item])
        else:
            bitmap = self.bitmaps[item]
        dc.DrawBitmap(bitmap, x + 2, y + 4, True)

    def OnMeasureItem(self, item):
        return 1 if item == wx.NOT_FOUND \
            else self.bitmaps[item].GetSize()[1] + 7

    def OnMeasureItemWidth(self, item):
        return 1 if item == wx.NOT_FOUND \
            else self.bitmaps[item].GetSize()[0] - 4

    def _create_items(self):
        return [str(item) for item in range(len(self.bitmaps))]

    def set_bitmaps(self, bitmaps):
        self.bitmaps = bitmaps
        self.SetItems(self._create_items())

    def set_items(self, items):
        self.SetItems(items)

    def set_selection(self, index):
        if index < self.GetCount():
            self.SetSelection(index)

    def get_selection(self):
        return self.GetSelection()

    def set_active(self, index):
        self.set_selection(index)

    def get_active(self):
        return self.get_selection()


class Combobox(wx.ComboBox, DataWidgetMixin):
    items = None
    callback = None
    flag = False

    def __init__(self, parent, value='', pos=(-1, 1), size=DEF_SIZE, width=0,
                 items=None, onchange=None):
        items = items or []
        self.items = [tr(item) for item in items]
        flags = wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER
        size = self._set_width(size, width)
        wx.ComboBox.__init__(self, parent, wx.ID_ANY, value,
                             pos, size, items, flags)
        if onchange:
            self.callback = onchange
            self.Bind(wx.EVT_COMBOBOX, self.on_change, self)
            self.Bind(wx.EVT_TEXT_ENTER, self.on_enter, self)
        self.Bind(wx.EVT_TEXT, self.on_typing, self)

    def on_typing(self, event):
        event.Skip()

    def on_change(self, event):
        if self.flag:
            return
        if self.callback:
            self.callback()
        event.Skip()

    def on_enter(self, event):
        if self.flag:
            return
        if self.callback:
            self.callback()
        event.Skip()

    def set_items(self, items):
        self.items = [tr(item) for item in items]
        self.SetItems(self.items)


class FloatCombobox(Combobox):
    digits = 0

    def __init__(self, parent, value='', width=5, digits=1,
                 items=None, onchange=None):
        items = items or []
        vals = [str(item) for item in items]
        Combobox.__init__(self, parent, str(value), width=width,
                          items=vals, onchange=onchange)
        self.digits = digits

    def on_typing(self, event):
        if self.flag:
            return
        txt = Combobox.get_value(self)
        res = ''
        for item in txt:
            chars = '.0123456789'
            if not self.digits:
                chars = '0123456789'
            if item in chars:
                res += item
        if not txt == res:
            self.flag = True
            Combobox.set_value(self, res)
            self.flag = False
        event.Skip()

    def get_value(self):
        val = Combobox.get_value(self) or 1
        return float(val) if self.digits else int(val)

    def set_value(self, val):
        val = str(val)
        if not val == Combobox.get_value(self):
            Combobox.set_value(self, val)

    def set_items(self, items):
        self.SetItems([str(item) for item in items])


class Entry(wx.TextCtrl, DataWidgetMixin):
    my_changes = False
    value = ''
    _callback = None
    _callback1 = None
    editable = True

    def __init__(self, parent, value='', size=DEF_SIZE, width=0, onchange=None,
                 multiline=False, richtext=False, onenter=None, editable=True,
                 no_border=False, no_wrap=False):
        self.value = tr(value)
        self.editable = editable
        self._callback = onchange
        style = wx.TE_MULTILINE if multiline else 0
        style = style | wx.TE_RICH2 if richtext else style
        style = style | wx.NO_BORDER if no_border else style
        style = style | wx.TE_PROCESS_ENTER if onenter else style
        style = style | wx.TE_DONTWRAP if no_wrap else style

        size = self._set_width(size, width)
        wx.TextCtrl.__init__(
            self, parent, wx.ID_ANY, self.value, size=size, style=style)
        if onenter:
            self._callback1 = onenter
            self.Bind(wx.EVT_TEXT_ENTER, self._on_enter, self)
        if multiline:
            self.ScrollPages(0)
        self.SetEditable(editable)
        self.Bind(wx.EVT_TEXT, self._on_change, self)

    def get_cursor_pos(self):
        return self.GetInsertionPoint()

    def set_cursor_pos(self, pos):
        pos = 0 if pos < 0 else pos
        pos = len(self.value) if pos > len(self.value) else pos
        self.SetInsertionPoint(pos)

    def _on_change(self, event):
        if self.my_changes:
            self.my_changes = False
        else:
            self.value = self.GetValue()
            if self._callback:
                self._callback()
        event.Skip()

    def _on_enter(self, event):
        event.StopPropagation()
        self.value = self.GetValue()
        if self._callback1:
            self._callback1()

    def set_value(self, val):
        self.my_changes = True
        self.value = tr(val)
        self.SetValue(self.value)

    def set_editable(self, val):
        self.SetEditable(val)

    def set_text_colors(self, fg=(), bg=()):
        fg = wx.Colour(*fg) if fg else wx.NullColour
        bg = wx.Colour(*bg) if bg else wx.NullColour
        self.SetDefaultStyle(wx.TextAttr(fg, bg))

    def set_monospace(self, zoom=0):
        points = self.GetFont().GetPointSize()
        f = wx.Font(points + zoom, wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.SetDefaultStyle(wx.TextAttr(wx.NullColour, wx.NullColour, f))

    def append(self, txt):
        self.AppendText(tr(txt))
        self.value = self.GetValue()

    def clear(self):
        self.Clear()
        self.value = ''


class NativeSpin(wx.SpinCtrl, RangeDataWidgetMixin):
    callback = None
    callback1 = None
    flag = True
    ctxmenu_flag = False

    def __init__(self, parent, value=0, range_val=(0, 1), size=DEF_SIZE,
                 width=6, onchange=None, onenter=None, check_focus=True):
        width = 0 if const.IS_GTK3 else width
        width = width + 2 if const.IS_MSW else width
        size = self._set_width(size, width)
        style = wx.SP_ARROW_KEYS | wx.ALIGN_LEFT | wx.TE_PROCESS_ENTER
        wx.SpinCtrl.__init__(self, parent, wx.ID_ANY, '',
                             size=size, style=style)
        self.set_range(range_val)
        self.set_value(value)
        if onchange:
            self.callback = onchange
            self.Bind(wx.EVT_SPINCTRL, self.on_change, self)
        if onenter:
            self.callback1 = onenter
            self.Bind(wx.EVT_TEXT_ENTER, self.on_enter, self)
        if check_focus:
            self.Bind(wx.EVT_KILL_FOCUS, self._entry_lost_focus, self)
            self.Bind(wx.EVT_CONTEXT_MENU, self._ctxmenu, self)

    def on_change(self, *args):
        if self.callback:
            self.callback()

    def on_enter(self, event):
        if self.callback1:
            self.callback1()
        event.Skip()

    def _ctxmenu(self, event):
        self.ctxmenu_flag = True
        event.Skip()

    def _entry_lost_focus(self, event):
        if not self.flag and not self.ctxmenu_flag:
            self.on_change()
        elif not self.flag and self.ctxmenu_flag:
            self.ctxmenu_flag = False
        event.Skip()

    def get_value(self):
        return int(self.GetValue())

    def set_value(self, value):
        self.SetValue(int(value))


NativeSpinDouble = NativeSpin

if not const.IS_WX2:
    class NativeSpinDouble(wx.SpinCtrlDouble, RangeDataWidgetMixin):
        callback = None
        callback1 = None
        flag = True
        ctxmenu_flag = False
        digits = 2
        step = 0

        def __init__(
                self, parent, value=0.0, range_val=(0.0, 1.0), step=0.01,
                digits=2, size=DEF_SIZE, width=6,
                onchange=None, onenter=None, check_focus=True):

            self.range_val = range_val
            width = 0 if const.IS_GTK3 else width
            width = width + 2 if const.IS_MSW else width
            size = self._set_width(size, width)
            style = wx.SP_ARROW_KEYS | wx.ALIGN_LEFT | wx.TE_PROCESS_ENTER
            wx.SpinCtrlDouble.__init__(self, parent, wx.ID_ANY, '',
                                       size=size, style=style,
                                       min=0, max=100, initial=value, inc=step)
            self.set_range(range_val)
            self.set_value(value)
            self.set_step(step)
            self.set_digits(digits)
            if onchange:
                self.callback = onchange
                self.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_change, self)
            if onenter:
                self.callback1 = onenter
                self.Bind(wx.EVT_TEXT_ENTER, self.on_enter, self)
            if check_focus:
                self.Bind(
                    wx.EVT_KILL_FOCUS, self._entry_lost_focus, self)
                self.Bind(wx.EVT_CONTEXT_MENU, self._ctxmenu, self)

        def set_step(self, step):
            self.step = step
            self.SetIncrement(step)

        def set_digits(self, digits):
            self.digits = digits
            self.SetDigits(digits)

        def _set_digits(self, digits):
            self.set_digits(digits)

        def on_change(self, *args):
            if self.callback:
                self.callback()

        def on_enter(self, event):
            if self.callback1:
                self.callback1()
            event.Skip()

        def _ctxmenu(self, event):
            self.ctxmenu_flag = True
            event.Skip()

        def _entry_lost_focus(self, event):
            if not self.flag and not self.ctxmenu_flag:
                self.on_change()
            elif not self.flag and self.ctxmenu_flag:
                self.ctxmenu_flag = False
            event.Skip()

        def get_value(self):
            return float(self.GetValue()) if self.digits \
                else int(self.GetValue())

        def set_value(self, value):
            self.SetValue(float(value) if self.digits else int(value))


class NativeSpinButton(wx.SpinButton, RangeDataWidgetMixin):
    def __init__(
            self, parent, value=0, range_val=(0, 10), size=DEF_SIZE,
            onchange=None, vertical=True):
        self.range_val = range_val
        style = wx.SL_VERTICAL
        if not vertical:
            style = wx.SL_HORIZONTAL
        wx.SpinButton.__init__(self, parent, wx.ID_ANY, size=size, style=style)
        self.SetValue(value)
        self.SetRange(*range_val)
        if onchange:
            self.Bind(wx.EVT_SPIN, onchange, self)


class DummyEvent(object):
    def Skip(self): pass


_dummy_event = DummyEvent()


class _MBtn(basic.Panel, basic.SensitiveCanvas):
    _pressed = False
    _enabled = True
    _active = True
    _top = True
    parent = None
    callback = None
    callback_wheel = None
    points = None

    def __init__(self, parent, size, top=True, onclick=None, onwheel=None):
        self._top = top
        self.callback = onclick
        self.callback_wheel = onwheel
        self.parent = parent
        basic.Panel.__init__(self, parent, wx.ID_ANY)
        basic.SensitiveCanvas.__init__(self)
        self.set_size(size)
        self.points = self._get_points()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._repeat_on_timer)

    def _get_points(self):
        w, h = self.GetSizeTuple()
        mx = 6
        my = h // 2 + 4
        s = 3
        points = [(mx - s, my), (mx + s, my), (mx, my - s), (mx - s, my)]
        if not self._top:
            my = h // 2 - 4
            points = [(mx - s, my), (mx + s, my), (mx, my + s), (mx - s, my)]
        return points

    def _repeat_on_timer(self, event):
        if self._pressed and self._enabled:
            self.btn_down()
            self.refresh()
        else:
            if self.timer.IsRunning():
                self.timer.Stop()

    def set_enable(self, value):
        self._enabled = value
        self._pressed = False if not value else self._pressed
        self.refresh()

    def get_enabled(self):
        return self._enabled

    def set_active(self, value):
        self._active = value
        self._pressed = False if not value else self._pressed
        self.refresh()

    def get_active(self):
        return self._active

    def mouse_left_down(self, point):
        if self._enabled:
            self._pressed = True
            self.btn_down()
        self.timer.Start(200)
        self.refresh()

    def mouse_left_up(self, point):
        self._pressed = False
        self.refresh()

    def mouse_wheel(self, val):
        if self.callback_wheel and self._enabled:
            self.callback_wheel(val)

    def btn_down(self):
        if self.callback:
            self.callback()

    def paint(self):
        w, h = self.GetSizeTuple()
        x = -20
        y = 0 if self._top else -h
        flag = wx.CONTROL_DIRTY
        if self._pressed and self._enabled:
            flag = wx.CONTROL_PRESSED | wx.CONTROL_SELECTED
        elif not self._enabled:
            flag = wx.CONTROL_DIRTY | wx.CONTROL_DISABLED

        # Draw button bg
        self.set_stroke()
        self.set_fill(const.UI_COLORS['bg'])
        self.draw_rounded_rect(x, y, w - x, 2 * h, 3)

        # Draw button
        nr = wx.RendererNative.Get()
        nr.DrawPushButton(self, self.pdc, (x, y, w - x, 2 * h), flag)

        # Drawing signs
        self.set_gc_stroke()
        self.set_gc_fill(const.UI_COLORS['text']
                         if self._enabled and self._active
                         else const.UI_COLORS['disabled_text'])
        self.gc_draw_polygon(self.points)


class MegaSpinButton(basic.Panel):
    enabled = True
    width = 14

    def __init__(self, parent, value=0, range_val=(0, 10), size=DEF_SIZE,
                 onchange=None, vertical=True):
        self.range_val = range_val
        self.value = value
        self.callback = onchange
        size = (self.width, 20) if size == DEF_SIZE else (self.width, size[1])
        basic.Panel.__init__(self, parent, wx.ID_ANY)
        self.set_size(size)
        w, h = size
        my = h // 2
        self.top_btn = _MBtn(self, (w, my),
                             onclick=self._top_btn_down,
                             onwheel=self._mouse_wheel)
        self.top_btn.SetPosition((0, 0))
        self.bottom_btn = _MBtn(self, (w, h - my), False,
                                onclick=self._bottom_btn_down,
                                onwheel=self._mouse_wheel)
        self.bottom_btn.SetPosition((0, my))
        self._check_range()

    def Enable(self, val):
        self.enabled = val
        self.top_btn.set_enable(val)
        self.bottom_btn.set_enable(val)

    def get_value(self):
        return self.value

    def set_value(self, val):
        self.value = val
        self._check_range()

    def set_range(self, range_val):
        self.range_val = range_val
        self._check_range()

    def _check_range(self):
        if self.value == self.range_val[0]:
            self.bottom_btn.set_active(False)
        elif not self.bottom_btn.get_active():
            self.bottom_btn.set_active(True)
        if self.value == self.range_val[1]:
            self.top_btn.set_active(False)
        elif not self.top_btn.get_active():
            self.top_btn.set_active(True)

    def _mouse_wheel(self, val):
        if not self.enabled:
            return
        if val < 0:
            self._bottom_btn_down()
        else:
            self._top_btn_down()

    def _top_btn_down(self):
        if self.value < self.range_val[1]:
            self.value += 1
            if self.callback:
                self.callback(_dummy_event)
        self._check_range()

    def _bottom_btn_down(self):
        if self.value > self.range_val[0]:
            self.value -= 1
            if self.callback:
                self.callback(_dummy_event)
        self._check_range()


if const.IS_GTK3:
    SpinButton = MegaSpinButton
else:
    SpinButton = NativeSpinButton


class MegaSpinDouble(wx.Panel, RangeDataWidgetMixin):
    entry = None
    sb = None
    line = None

    flag = True
    ctxmenu_flag = False
    value = 0.0
    range_val = (0.0, 1.0)
    step = 0.01
    digits = 2
    callback = None
    enter_callback = None

    def __init__(
            self, parent, value=0.0, range_val=(0.0, 1.0), step=0.01,
            digits=2, size=DEF_SIZE, width=5,
            onchange=None, onenter=None, check_focus=True):

        self.callback = onchange
        self.enter_callback = onenter
        spin_overlay = const.SPIN['overlay']
        spin_sep = const.SPIN['sep']
        if const.IS_MAC:
            spin_overlay = False
        if not width and const.IS_MSW:
            width = 5

        wx.Panel.__init__(self, parent)
        if spin_overlay:
            if const.IS_GTK:
                self.entry = Entry(
                    self, '', size=size, width=width,
                    onchange=self._check_entry, onenter=self._entry_enter)
                size = (-1, self.entry.GetSize()[1])
                self.entry.SetPosition((0, 0))
                self.sb = SpinButton(self, size=size, onchange=self._check_spin)
                w_pos = self.entry.GetSize()[0] - 5
                if spin_sep:
                    self.line = HPanel(self)
                    self.line.SetSize((1, self.sb.GetSize()[1] - 2))
                    self.line.set_bg(const.UI_COLORS['hover_solid_border'])
                    self.line.SetPosition((w_pos - 1, 1))
                self.sb.SetPosition((w_pos, 0))
                self.SetSize((-1, self.entry.GetSize()[1]))
            elif const.IS_MSW:
                width += 2
                self.entry = Entry(
                    self, '', size=size, width=width,
                    onchange=self._check_entry, onenter=self._entry_enter)
                size = (-1, self.entry.GetSize()[1] - 3)
                self.sb = SpinButton(
                    self.entry, size=size, onchange=self._check_spin)
                w_pos = self.entry.GetSize()[0] - self.sb.GetSize()[0] - 3
                self.sb.SetPosition((w_pos, 0))
                w, h = self.entry.GetSize()
                self.entry.SetSize((w, h + 1))

        else:
            self.box = wx.BoxSizer(const.HORIZONTAL)
            self.SetSizer(self.box)
            self.entry = Entry(
                self, '', size=size, width=width,
                onchange=self._check_entry, onenter=self._entry_enter)
            self.box.Add(self.entry, 0, wx.ALL)
            size = (-1, self.entry.GetSize()[1])
            self.sb = SpinButton(self, size=size, onchange=self._check_spin)
            self.box.Add(self.sb, 0, wx.ALL)

        if check_focus:
            self.entry.Bind(
                wx.EVT_KILL_FOCUS, self._entry_lost_focus, self.entry)
            self.entry.Bind(wx.EVT_CONTEXT_MENU, self._ctxmenu, self.entry)

        self.set_step(step)
        self.set_range(range_val)
        self._set_digits(digits)
        self._set_value(value)
        self.flag = False
        self.Fit()
        self.Bind(wx.EVT_MOUSEWHEEL, self._mouse_wheel)

    def set_enable(self, val):
        self.entry.Enable(val)
        self.sb.Enable(val)
        if self.line:
            color = const.UI_COLORS['hover_solid_border'] if val \
                else const.UI_COLORS['light_shadow']
            self.line.set_bg(color)

    def get_enabled(self):
        return self.entry.IsEnabled()

    def _check_spin(self, event):
        if self.flag:
            return
        coef = pow(10, self.digits)
        dval = float(self.sb.get_value() - int(self.value * coef))
        if not self.value == self._calc_entry():
            self._set_value(self._calc_entry())
        self.SetValue(dval * self.step + self.value)
        event.Skip()

    def _entry_enter(self):
        if self.flag:
            return
        self.SetValue(self._calc_entry())
        if self.enter_callback:
            self.enter_callback()

    def _mouse_wheel(self, event):
        if self.get_enabled():
            if event.GetWheelRotation() < 0:
                self.SetValue(self._calc_entry() - self.step)
            else:
                self.SetValue(self._calc_entry() + self.step)

    def _ctxmenu(self, event):
        self.ctxmenu_flag = True
        event.Skip()

    def _entry_lost_focus(self, event):
        if not self.flag and not self.ctxmenu_flag:
            self.SetValue(self._calc_entry())
        elif not self.flag and self.ctxmenu_flag:
            self.ctxmenu_flag = False
        event.Skip()

    def _check_entry(self):
        if not self.flag:
            value = self.entry.get_value()
            chars = '.0123456789+-*/' if self.digits else '0123456789+-*/'
            result = ''.join([item for item in value if item in chars])
            if not value == result:
                self.flag = True
                self.entry.set_value(result)
                self.flag = False

    def _calc_entry(self):
        txt = self.entry.get_value()
        val = 0
        try:
            line = 'val=' + txt
            code = compile(line, '<string>', 'exec')
            exec code
        except Exception:
            return self.value
        return val

    def _check_in_range(self, val):
        minval, maxval = self.range_val
        if val < minval:
            val = minval
        if val > maxval:
            val = maxval
        coef = pow(10, self.digits)
        val = round(val * coef) / coef
        return val

    def _set_value(self, val):
        coef = pow(10, self.digits)
        self.value = self._check_in_range(val)
        if not self.digits:
            self.value = int(self.value)
        self.entry.set_value(str(self.value))
        self.sb.set_value(int(self.value * coef))

    def _set_digits(self, digits):
        self.digits = digits
        self.set_range(self.range_val)

    def set_value(self, val):
        self.flag = True
        self._set_value(val)
        self.flag = False

    # ----- Native API emulation
    def SetValue(self, val):
        self.flag = True
        old_value = self.value
        self._set_value(val)
        self.flag = False
        if self.callback is not None and not self.value == old_value:
            self.callback()

    def GetValue(self):
        if not self.value == self._calc_entry():
            self._set_value(self._calc_entry())
        return self.value

    def SetRange(self, minval, maxval):
        coef = pow(10, self.digits)
        self.range_val = (minval, maxval)
        self.sb.set_range((int(minval * coef), int(maxval * coef)))

    # ----- Control API
    def set_step(self, step):
        self.step = step

    def set_digits(self, digits):
        self._set_digits(digits)
        self.SetValue(self.value)


class MegaSpin(MegaSpinDouble):
    def __init__(self, parent, value=0, range_val=(0, 1), size=DEF_SIZE,
                 width=5, onchange=None, onenter=None, check_focus=True):
        MegaSpinDouble.__init__(self, parent, value, range_val, 1, 0, size,
                                 width, onchange, onenter, check_focus)

    def set_digits(self, digits):
        pass


IntSpin = MegaSpin
FloatSpin = MegaSpinDouble


class Slider(wx.Slider, RangeDataWidgetMixin):
    callback = None
    final_callback = None

    def __init__(
            self, parent, value=0, range_val=(1, 100),
            size=(100, -1), vertical=False, onchange=None,
            on_final_change=None):
        self.range_val = range_val
        style = 0
        if vertical:
            style |= wx.SL_VERTICAL
            if size == (100, -1):
                size = (-1, 100)
        else:
            style |= wx.SL_HORIZONTAL
        start, end = range_val
        wx.Slider.__init__(
            self, parent, wx.ID_ANY, value, start,
            end, size=size, style=style)
        if onchange:
            self.callback = onchange
            self.Bind(wx.EVT_SCROLL, self._onchange, self)
        if on_final_change:
            self.final_callback = on_final_change
            self.Bind(wx.EVT_LEFT_UP, self._on_final_change, self)
            self.Bind(wx.EVT_RIGHT_UP, self._on_final_change, self)

    def _onchange(self, event):
        if self.callback:
            self.callback()

    def _on_final_change(self, event):
        event.Skip()
        if self.final_callback:
            self.final_callback()


class Splitter(wx.SplitterWindow, WidgetMixin):
    def __init__(self, parent, live_update=True):
        style = wx.SP_NOBORDER
        style = style | wx.SP_LIVE_UPDATE if live_update else style
        wx.SplitterWindow.__init__(self, parent, wx.ID_ANY, style=style)

    def split_vertically(self, win1, win2, sash_pos=0):
        self.SplitVertically(win1, win2, sash_pos)

    def split_horizontally(self, win1, win2, sash_pos=0):
        self.SplitHorizontally(win1, win2, sash_pos)

    def set_min_size(self, size):
        self.SetMinimumPaneSize(size)

    def get_pane_size(self):
        return self.GetSashPosition()

    def unsplit(self, remove_win=None):
        self.Unsplit(remove_win)

    def set_sash_gravity(self, val):
        self.SetSashGravity(val)

    def set_sash_position(self, val):
        self.SetSashPosition(val)

    def get_sash_position(self):
        return self.GetSashPosition()


class ScrollBar(wx.ScrollBar, WidgetMixin):
    callback = None
    autohide = False

    def __init__(self, parent, vertical=True, onscroll=None, autohide=False):
        style = wx.SB_VERTICAL if vertical else wx.SB_HORIZONTAL
        wx.ScrollBar.__init__(self, parent, wx.ID_ANY, style=style)
        self.callback = onscroll
        self.autohide = autohide
        self.Bind(wx.EVT_SCROLL, self._scrolling, self)

    def set_scrollbar(self, pos, thumbsize, rng, pagesize, refresh=True):
        self.SetScrollbar(pos, thumbsize, rng, pagesize, refresh)

    def set_callback(self, callback):
        self.callback = callback

    def _scrolling(self, *args):
        if self.callback:
            self.callback()

    def get_thumb_pos(self):
        return self.GetThumbPosition()


class ColorButton(wx.ColourPickerCtrl, WidgetMixin):
    callback = None
    silent = True

    def __init__(self, parent, color=(), onchange=None, silent=True):
        self.silent = silent
        if not color:
            color = const.BLACK
        elif isinstance(color, str):
            color = wx.Colour(*self.hex_to_val255(color))
        else:
            color = wx.Colour(*self.val255(color))
        wx.ColourPickerCtrl.__init__(self, parent, wx.ID_ANY, color)
        if onchange:
            self.callback = onchange
            self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.on_change, self)

    def on_change(self, event):
        if self.callback:
            self.callback()

    def hex_to_val255(self, hexcolor):
        return tuple(int(hexcolor[a:b], 0x10)
                     for a, b in ((1, 3), (3, 5), (5, -1)))

    def val255(self, vals):
        return tuple(int(item * 255) for item in vals)

    def val255_to_dec(self, vals):
        return tuple(item / 255.0 for item in vals)

    def set_value(self, color):
        self.SetColour(wx.Colour(*self.val255(color)))
        if not self.silent:
            self.on_change(None)

    def set_value255(self, color):
        self.SetColour(wx.Colour(*color))
        if not self.silent:
            self.on_change(None)

    def get_value(self):
        return self.val255_to_dec(self.GetColour().Get())

    def get_value255(self):
        return self.GetColour().Get()


class AnimatedGif(animate.GIFAnimationCtrl):
    def __init__(self, parent, filepath):
        animate.GIFAnimationCtrl.__init__(self, parent, wx.ID_ANY, tr(filepath))
        self.GetPlayer().UseBackgroundColour(True)

    def stop(self): self.Stop()

    def play(self): self.Play()


class ProgressBar(wx.Gauge, WidgetMixin):
    def __init__(self, parent):
        size = (400, 15)
        wx.Gauge.__init__(self, parent, range=100, size=size,
                          style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)
        self.SetRange(100)

    def set_value(self, val):
        if val < 0:
            return self.pulse()
        self.SetValue(int(val))
        self.Update()

    def set_dec_value(self, val):
        self.set_value(val * 100)

    def get_value(self):
        return self.GetValue()

    def pulse(self):
        self.Pulse()
