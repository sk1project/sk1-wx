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

import logging
import wx

import const
import mixins
from basic import HPanel, VPanel
from const import EXPAND, ALL, VERTICAL, HORIZONTAL, tr
from widgets import HLine, Button, Label, ProgressBar

LOG = logging.getLogger(__name__)


class ProgressDialog(wx.ProgressDialog):

    def __init__(self, parent=None, title='', width=130):
        style = wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
        wx.ProgressDialog.__init__(self, tr(title), ' ' * width,
                                   parent=parent, style=style)

    def update(self, value, msg):
        self.Update(value, tr(msg))

    def destroy(self):
        self.Destroy()


class SimpleDialog(wx.Dialog, mixins.DialogMixin):
    _timer = None
    add_line = True

    def __init__(self, parent, title, size=(-1, -1), style=VERTICAL,
                 resizable=False, on_load=None, add_line=True, margin=None):
        stl = wx.DEFAULT_DIALOG_STYLE
        stl = stl | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX if resizable else stl
        self.add_line = add_line

        wx.Dialog.__init__(self, parent, -1, tr(title), wx.DefaultPosition,
                           size, style=stl)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        if margin is None:
            margin = 5 if const.IS_GTK else 10

        self.box = VPanel(self)
        sizer.Add(self.box, 1, ALL | EXPAND, margin)

        if style == HORIZONTAL:
            self.panel = HPanel(self.box)
        else:
            self.panel = VPanel(self.box)
        self.box.pack(self.panel, expand=True, fill=True)

        self.build()
        self.set_dialog_buttons()
        if size == (-1, -1):
            self.Fit()
        self.CenterOnParent()
        self.panel.layout()
        self.Bind(wx.EVT_CLOSE, self.on_close, self)
        if on_load:
            self._timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, on_load)
            self._timer.Start(200)

    def build(self):
        pass

    def set_dialog_buttons(self):
        pass

    def get_result(self):
        return None

    def on_close(self, event=None):
        self.end_modal(const.BUTTON_CANCEL)

    def pack(self, *args, **kw):
        obj = args[0]
        if not obj.GetParent() == self.panel:
            obj.Reparent(self.panel)
        self.panel.pack(*args, **kw)

    def show(self):
        self.show_modal()
        self.destroy()


class CloseDialog(SimpleDialog):
    button_box = None
    close_btn = None
    left_button_box = None

    def __init__(self, parent, title, size=(-1, -1), style=VERTICAL,
                 resizable=True, on_load=None, add_line=True, margin=None):
        SimpleDialog.__init__(self, parent, title, size, style, resizable,
                              on_load, add_line, margin)

    def set_dialog_buttons(self):
        if self.add_line:
            self.box.pack(HLine(self.box), fill=True, padding=5)
        else:
            self.box.pack((3, 3))

        self.button_box = HPanel(self.box)
        self.box.pack(self.button_box, fill=True)

        self.close_btn = Button(self.button_box, '', onclick=self.on_close,
                                default=True, pid=const.BUTTON_CLOSE)

        self.left_button_box = HPanel(self.button_box)
        self.button_box.pack(self.left_button_box, expand=True, fill=True)
        self.button_box.pack(self.close_btn, padding=5)


class OkCancelDialog(SimpleDialog):
    sizer = None
    box = None
    button_box = None
    ok_btn = None
    cancel_btn = None
    action_button = None
    left_button_box = None
    button_box_padding = 0

    def __init__(self, parent, title, size=(-1, -1), style=VERTICAL,
                 resizable=False, action_button=const.BUTTON_OK, on_load=None,
                 add_line=True, margin=None, button_box_padding=0):
        self.action_button = action_button
        self.button_box_padding = button_box_padding
        SimpleDialog.__init__(self, parent, title, size, style, resizable,
                              on_load, add_line, margin)

    def set_dialog_buttons(self):
        if self.add_line:
            self.box.pack(HLine(self.box), fill=True, padding=5)
        else:
            self.box.pack((3, 3))

        self.button_box = HPanel(self.box)
        self.box.pack(self.button_box, fill=True,
                      padding_all=self.button_box_padding)

        self.ok_btn = Button(self.button_box, '', onclick=self.on_ok,
                             default=True, pid=self.action_button)
        self.cancel_btn = Button(self.button_box, '', onclick=self.on_cancel,
                                 pid=const.BUTTON_CANCEL)

        self.left_button_box = HPanel(self.button_box)
        self.button_box.pack(self.left_button_box, expand=True, fill=True)

        if const.IS_MAC:
            self.button_box.pack(self.ok_btn, padding=5)
            self.button_box.pack(self.cancel_btn, padding=5)
        elif const.IS_MSW:
            self.button_box.pack(self.ok_btn, padding=2)
            self.button_box.pack(self.cancel_btn)
        else:
            self.button_box.pack(self.cancel_btn, padding=2)
            self.button_box.pack(self.ok_btn)

    def on_ok(self):
        self.end_modal(const.BUTTON_OK)

    def on_cancel(self):
        self.end_modal(const.BUTTON_CANCEL)

    def show(self):
        ret = self.get_result() if self.show_modal() == const.BUTTON_OK \
            else None
        self.destroy()
        return ret


class CustomProgressDialog(SimpleDialog):
    label = None
    progressbar = None
    button_box = None
    cancel_btn = None
    result = None
    callback = None
    args = None
    msg = ''

    def __init__(self, parent, title, size=(500, 100), style=VERTICAL,
                 resizable=False, action_button=const.BUTTON_CANCEL,
                 add_line=False, margin=None,
                 button_box_padding=0):
        self.label = title
        self.action_button = action_button
        self.button_box_padding = button_box_padding
        SimpleDialog.__init__(self, parent, title, size, style, resizable,
                              self.on_load, add_line, margin)

    def build(self):
        self.panel.pack((5, 5))
        self.label = Label(self.panel, self.label)
        self.panel.pack(self.label, fill=True)
        self.progressbar = ProgressBar(self.panel)
        self.panel.pack(self.progressbar, fill=True, padding=15)

    def set_dialog_buttons(self):
        self.button_box = HPanel(self.box)
        self.box.pack(self.button_box, fill=True,
                      padding_all=self.button_box_padding)
        self.button_box.pack(HPanel(self.button_box), fill=True, expand=True)
        self.cancel_btn = Button(self.button_box, '', onclick=self.on_cancel,
                                 default=True, pid=const.BUTTON_CANCEL)
        self.cancel_btn.set_enable(False)
        self.button_box.pack(self.cancel_btn)
        self.fit()

    def on_cancel(self):
        self.end_modal(const.BUTTON_CANCEL)

    def show(self):
        self.show_modal()
        return self.result

    def update_data(self, value, msg):
        self.label.set_text(msg)
        self.label.Update()
        self.progressbar.set_value(value)
        self.progressbar.Update()
        self.Update()
        wx.Yield()

    def on_load(self, *args):
        self._timer.Stop()
        self.progressbar.set_value(5)
        try:
            if self.callback and self.args:
                self.result = self.callback(*self.args)
        except Exception as e:
            LOG.exception('Error in progress dialog running: %s', e)
        finally:
            self.progressbar.set_value(98)
            self.end_modal(const.BUTTON_CANCEL)

    def run(self, callback, args):
        self.callback, self.args = callback, args
        return self.show()
