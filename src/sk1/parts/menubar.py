# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2018 by Ihor E. Novikov
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

import wal
from sk1 import _, config, events
from sk1.resources import pdids
from sk1.pwidgets.ctxmenu import ActionMenuItem

LOG = logging.getLogger(__name__)


class AppMenuBar(wal.MenuBar):
    def __init__(self, app, mw):
        self.app = app
        self.mw = mw
        wal.MenuBar.__init__(self)
        self.entries = []

        # ---File menu
        sub = (wal.ID_NEW, pdids.ID_NEW_FROM_TEMPLATE, None, wal.ID_OPEN,
               (_("Open &Recent"), (HistoryMenu(self.app, self.mw),)),
               pdids.ID_VIEW_LOG, None,
               wal.ID_SAVE, wal.ID_SAVEAS, pdids.ID_SAVE_SEL, pdids.ID_SAVEALL,
               None, wal.ID_CLOSE, pdids.ID_CLOSE_OTHERS, wal.ID_CLOSE_ALL,
               None, pdids.ID_IMPORT, pdids.ID_EXPORT, None, wal.ID_PRINT,
               None, wal.ID_EXIT,)
        entry = (_("&File"), sub)
        self.entries.append(entry)

        # ---Edit menu
        sub = (wal.ID_UNDO, wal.ID_REDO, pdids.ID_CLEAR_UNDO, None, wal.ID_CUT,
               wal.ID_COPY, wal.ID_PASTE, wal.ID_DELETE, pdids.ID_DUPLICATE,
               None, wal.ID_SELECTALL, pdids.ID_DESELECT, pdids.ID_INV_SELECT,
               None, pdids.FILL_MODE, pdids.COPY_FILL, pdids.STROKE_MODE,
               pdids.COPY_STROKE, None, pdids.ID_LOCK_GUIDES,
               None, wal.ID_PROPERTIES, wal.ID_PREFERENCES,)
        entry = (_("&Edit"), sub)
        self.entries.append(entry)

        # ---View menu
        sub = (pdids.ID_STROKE_VIEW, pdids.ID_DRAFT_VIEW,
               pdids.ID_SIMULATE_PRINTER, None,
               wal.ID_ZOOM_100, wal.ID_ZOOM_IN, wal.ID_ZOOM_OUT,
               pdids.ID_PREV_ZOOM, None,
               pdids.ID_ZOOM_PAGE, wal.ID_ZOOM_FIT,
               None,
               (_("&Show"), (pdids.ID_SHOW_GRID, pdids.ID_SHOW_GUIDES,
                             pdids.ID_SHOW_SNAP, pdids.ID_SHOW_PAGE_BORDER)),
               None,
               (_("S&nap to"), (pdids.ID_SNAP_TO_GRID, pdids.ID_SNAP_TO_GUIDE,
                                pdids.ID_SNAP_TO_OBJ, pdids.ID_SNAP_TO_PAGE)),
               None, pdids.ID_ICONIZER,
               wal.ID_REFRESH,)
        entry = (_("&View"), sub)
        self.entries.append(entry)

        # ---Layout menu
        sub = (pdids.ID_INSERT_PAGE, pdids.ID_DELETE_PAGE, pdids.ID_GOTO_PAGE,
               None, pdids.ID_NEXT_PAGE, pdids.ID_PREV_PAGE,
               None, pdids.ID_TOOL_LAYERS,
               None, pdids.ID_PAGE_FRAME, pdids.ID_PAGE_GUIDE_FRAME,
               pdids.ID_GUIDES_AT_CENTER, pdids.ID_REMOVE_ALL_GUIDES,)
        entry = (_("&Layout"), sub)
        self.entries.append(entry)

        # ---Arrange menu
        sub = (
            (_("Trans&form"), (pdids.ID_POSITION_PLGN, pdids.ID_RESIZE_PLGN,
                               pdids.ID_SCALE_PLGN, pdids.ID_ROTATE_PLGN,
                               pdids.ID_SHEAR_PLGN,
                               None, pdids.ID_ROTATE_LEFT,
                               pdids.ID_ROTATE_RIGHT,
                               None, pdids.ID_MIRROR_H, pdids.ID_MIRROR_V)),
            pdids.ID_CLEAR_TRANSFORM, pdids.ID_INLINE_TRANSFORM,
            None, pdids.ID_ALIGN_PLGN,
            (_("&Order"), (pdids.ID_RAISE_TO_TOP, pdids.ID_RAISE,
                           pdids.ID_LOWER, pdids.ID_LOWER_TO_BOTTOM)),
            None, pdids.ID_COMBINE, pdids.ID_BREAK_APART,
            None, pdids.ID_GROUP, pdids.ID_UNGROUP, pdids.ID_UNGROUPALL, None,
            (_("&Shaping"), (pdids.ID_PATHS_TRIM, pdids.ID_PATHS_INTERSECTION,
                             pdids.ID_PATHS_EXCLUSION, pdids.ID_PATHS_FUSION)),
            None, pdids.ID_TO_CONTAINER, pdids.ID_FROM_CONTAINER,
            None, pdids.ID_TO_CURVES, pdids.ID_STROKE_TO_CURVES)
        entry = (_("&Arrange"), sub)
        self.entries.append(entry)

        # ---Paths menu
        sub = (pdids.ID_BEZIER_SEL_ALL_NODES, pdids.ID_BEZIER_REVERSE_ALL_PATHS,
               None, pdids.ID_BEZIER_SEL_SUBPATH_NODES,
               pdids.ID_BEZIER_DEL_SUBPATH,
               pdids.ID_BEZIER_REVERSE_SUBPATH, pdids.ID_BEZIER_EXTRACT_SUBPATH,
               None, pdids.ID_BEZIER_ADD_NODE, pdids.ID_BEZIER_DELETE_NODE,
               None, pdids.ID_BEZIER_ADD_SEG, pdids.ID_BEZIER_DELETE_SEG,
               pdids.ID_BEZIER_JOIN_NODE, pdids.ID_BEZIER_SPLIT_NODE,
               None, pdids.ID_BEZIER_SEG_TO_LINE, pdids.ID_BEZIER_SEG_TO_CURVE,
               None, pdids.ID_BEZIER_NODE_CUSP, pdids.ID_BEZIER_NODE_SMOOTH,
               pdids.ID_BEZIER_NODE_SYMMETRICAL,)
        entry = (_("&Paths"), sub)
        self.entries.append(entry)

        # ---Bitmaps menu
        sub = (
            pdids.ID_CONV_TO_CMYK, pdids.ID_CONV_TO_RGB,
            # pdids.ID_CONV_TO_LAB,
            pdids.ID_CONV_TO_GRAY, pdids.ID_CONV_TO_BW, None,
            pdids.ID_INVERT_BITMAP, None, pdids.ID_REMOVE_ALPHA,
            pdids.ID_INVERT_ALPHA, None, pdids.ID_EXTRACT_BITMAP)
        entry = (_("&Bitmaps"), sub)
        self.entries.append(entry)

        # ---Text menu
        sub = (pdids.ID_EDIT_TEXT, None, pdids.ID_TEXT_ON_PATH,
               pdids.ID_TEXT_ON_CIRCLE, pdids.ID_STRAIGHTEN_TEXT,
               None, pdids.ID_CLEAR_MARKUP, None, pdids.ID_UPPER_TEXT,
               pdids.ID_LOWER_TEXT, pdids.ID_CAPITALIZE_TEXT)
        entry = (_("&Text"), sub)
        self.entries.append(entry)

        # ---Help menu
        sub = (pdids.ID_REPORT_BUG, pdids.ID_CONSOLE, None,
               pdids.ID_APP_WEBSITE,
               pdids.ID_APP_FBPAGE,
               None, wal.ID_ABOUT,)
        entry = (_("&Help"), sub)
        self.entries.append(entry)

        self.create_menu(self, self.entries)

    def create_menu(self, parent, entries):
        for entry in entries:
            menu = wal.Menu()
            subentries = entry[1]
            for item in subentries:
                if item is None:
                    menu.append_separator()
                elif isinstance(item, wal.Menu):
                    menu = item
                elif isinstance(item, tuple):
                    self.create_menu(menu, (item,))
                else:
                    action = self.app.actions[item]
                    menuitem = ActionMenuItem(self.mw, menu, action)
                    menu.append_item(menuitem)
            parent.append_menu(wal.new_id(), entry[0], menu)


class HistoryMenu(wal.Menu):
    app = None
    mw = None
    items = None
    empty_item = None
    persistent_items = None

    def __init__(self, app, mw):
        self.app = app
        self.mw = mw
        wal.Menu.__init__(self)
        self.items = []
        self.persistent_items = []

        self.empty_item = wal.MenuItem(self, wal.new_id(), _('Empty'))

        self.items.append(self.append_separator())
        action = self.app.actions[pdids.ID_CLEAR_LOG]
        menuitem = ActionMenuItem(self.mw, self, action)
        self.append_item(menuitem)
        self.items.append(menuitem)

        self.persistent_items += self.items

        self.rebuild()
        events.connect(events.HISTORY_CHANGED, self.rebuild)

    def rebuild(self, *_args):
        class HistoryMenuItem(wal.MenuItem):
            app = None
            path = None

            def __init__(self, mw, parent, text, path):
                self.app = mw.app
                self.path = path
                item_id = wal.new_id()
                wal.MenuItem.__init__(self, parent, item_id, text)
                self.bind_to(mw, self.action, item_id)

            def action(self, _event):
                self.app.open(self.path)

        for item in self.items:
            self.remove_item(item)
        self.items = []
        if self.app.history.is_empty():
            self.items.append(self.empty_item)
            self.append_item(self.empty_item)
            self.empty_item.set_enable(False)
        else:
            entries = self.app.history.get_menu_entries()
            for entry in entries:
                menuitem = HistoryMenuItem(self.mw, self, entry[0], entry[1])
                self.items.append(menuitem)
                self.append_item(menuitem)
            for menuitem in self.persistent_items:
                self.items.append(menuitem)
                self.append_item(menuitem)



