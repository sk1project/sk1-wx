# -*- coding: utf-8 -*-
#
#  Copyright (C) 2011-2018 by Igor E. Novikov
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

from sk1 import events, appconst
from uc2 import uc2const
from uc2.uc2conf import UCConfig, UCData
from uc2.utils import system, fsutils


class AppData(UCData):
    app_name = 'sK1'
    app_proc = 'sk1'
    app_org = 'sK1 Project'
    app_domain = 'sk1project.net'
    app_icon = None
    doc_icon = None
    version = appconst.VERSION
    revision = appconst.REVISION
    app_config_dir = ''
    plugin_dir = ''
    app_palette_dir = ''
    app_temp_dir = ''
    plugin_dirs = []

    def __init__(self, app, cfgdir='~'):
        # --- Init paths
        path = fsutils.expanduser(os.path.join(cfgdir, '.config', 'sk1-wx'))
        self.app_config_dir = path

        UCData.__init__(self, app, check=False)
        self.check_config_dirs()

        self.app_palette_dir = os.path.join(path, 'palettes')
        self.plugin_dir = os.path.join(path, 'sk1_custom_plugins')
        self.app_temp_dir = os.path.join(path, 'temp')

        # --- Check config directories
        paths = (self.app_palette_dir, self.plugin_dir, self.app_temp_dir)
        [fsutils.makedirs(item) for item in paths if not fsutils.lexists(item)]

        plugin_dir_init = os.path.join(self.plugin_dir, '__init__.py')
        if not fsutils.lexists(plugin_dir_init):
            fsutils.get_fileptr(plugin_dir_init, True).close()


class AppConfig(UCConfig):
    def __init__(self):
        self.palette_files = {}
        UCConfig.__init__(self)

    def __setattr__(self, attr, value):
        if attr in ['filename', 'app']:
            self.__dict__[attr] = value
            return
        if not hasattr(self, attr) or getattr(self, attr) != value:
            self.__dict__[attr] = value
            events.emit(events.CONFIG_MODIFIED, attr, value)

    def get_defaults(self):
        defaults = AppConfig.__dict__.copy()
        defaults.update(UCConfig.get_defaults(self))
        return defaults

    # ============== Application pointer ===============
    app = None
    # ============== GENERIC SECTION ===================
    os = system.LINUX
    os_name = system.UBUNTU
    system_encoding = 'utf-8'  # default encoding (GUI uses utf-8 only)
    log_level = 'INFO'
    language = 'system'

    show_splash = False

    new_doc_on_start = False
    history_size = 100
    history_list_size = 10
    spin_overlay = True
    spin_sep = False
    spin_width = 0
    sash_position = -270
    make_backup = True
    make_export_backup = False
    active_plugins = None
    make_font_cache_on_start = False

    ui_style = appconst.GUI_CLASSIC
    tab_style = 0

    printer_config = {}

    # ===Ubuntu features
    ubuntu_global_menu = False
    ubuntu_scrollbar_overlay = False

    # ============== UI SECTION ===================
    mw_maximized = 0
    mw_size = (1000, 700)
    mw_min_size = (1000, 700)
    mw_width = 1000
    mw_height = 650
    mw_min_width = 1000
    mw_min_height = 650

    history_dlg_size = (500, 350)
    history_dlg_minsize = (500, 350)

    prefs_dlg_size = (700, 440)
    prefs_dlg_minsize = (700, 440)
    prefs_sash_pos = 200

    palinfo_dlg_size = (400, 350)
    palinfo_dlg_minsize = (400, 350)
    palcol_dlg_size = (600, 350)
    palcol_dlg_minsize = (600, 350)
    docprops_dlg_size = (510, 380)
    docprops_dlg_minsize = (510, 380)

    print_preview_dlg_size = (850, 650)
    print_preview_dlg_minsize = (850, 650)
    print_preview_dlg_maximized = False

    prnprops_dlg_size = (400, 500)
    prnprops_dlg_minsize = (400, 500)

    fill_dlg_size = (440, 370)
    fill_dlg_minsize = (440, 370)

    stroke_dlg_size = (430, 370)
    stroke_dlg_minsize = (430, 370)

    change_color_dlg_size = (420, 300)
    change_color_dlg_minsize = (420, 300)

    about_dlg_size = (550, 400)
    docinfo_dlg_size = (550, 400)
    dash_dlg_size = (300, 150)

    console_dlg_size = (800, 500)
    console_dlg_minsize = (800, 500)
    console_dlg_zoom = 0

    statusbar_fontsize = 0
    tabs_fontsize = 0
    tabs_use_bold = True
    set_doc_icon = True
    menu_size = (16, 16)
    toolbar_size = (24, 24)
    toolbar_icon_size = (24, 24)
    show_stub_buttons = True

    selected_text_bg = ()

    # ============== I/O SECTION ===================
    open_dir = '~'
    save_dir = '~'
    import_dir = '~'
    export_dir = '~'
    template_dir = '~'
    resource_dir = ''
    plugin_dirs = []
    profile_import_dir = '~'
    collection_dir = '~'
    print_dir = '~'
    log_dir = '~'

    # ============== MOUSE OPTIONS ================
    mouse_scroll_sensitivity = 3.0

    # ============== RULER OPTIONS ================
    ruler_size = 20
    ruler_font_size = 5
    ruler_text_vshift = 3
    ruler_text_hshift = 0
    ruler_bg = (1.0, 1.0, 1.0)
    ruler_fg = (0.0, 0.0, 0.0)
    ruler_small_tick = 5
    ruler_large_tick = 10

    # ============== PALETTE OPTIONS ================
    palette_hcell_height = 18
    palette_hcell_width = 40
    palette_vcell_height = 18
    palette_vcell_width = 18
    palette_orientation = uc2const.HORIZONTAL
    palette_expand = True
    palette = ''
    palette_files = {}

    # ============== CANVAS OPTIONS ================
    default_unit = uc2const.UNIT_MM

    obj_jump = 1.0 * uc2const.mm_to_pt
    page_border = 0.0

    sel_frame_visible = 1
    sel_frame_offset = 0.0
    sel_frame_color = (0.0, 0.0, 0.0)
    sel_frame_dash = [5, 5]

    sel_bbox_visible = 0
    sel_bbox_color = (0.0, 0.0, 0.0)
    sel_bbox_bgcolor = (1.0, 1.0, 1.0)
    sel_bbox_dash = [5, 5]

    sel_marker_size = 7.0
    sel_marker_frame_color = (0.62745, 0.62745, 0.64314)
    sel_marker_frame_bgcolor = (1.0, 1.0, 1.0)
    sel_marker_frame_dash = [5, 5]
    sel_marker_fill = (1.0, 1.0, 1.0)
    sel_marker_stroke = (0.0, 0.3, 1.0)
    sel_object_marker_color = (0.0, 0.0, 0.0)

    rotation_step = 5.0  # in degrees
    stroke_sensitive_size = 5.0  # in pixels

    # ============== SNAPPING OPTIONS ================
    snap_distance = 10.0  # in pixels
    snap_order = [appconst.SNAP_TO_GUIDES,
                  appconst.SNAP_TO_GRID,
                  appconst.SNAP_TO_OBJECTS,
                  appconst.SNAP_TO_PAGE]
    snap_to_grid = False
    snap_to_guides = True
    snap_to_objects = False
    snap_to_page = False

    show_snap = True
    snap_line_dash = [5, 5]
    snap_line_color = (1.0, 0.0, 0.0, 1.0)

    guide_line_dash = [5, 5]
    guide_line_dragging_color = (0.4, 0.73, 0.31)

    # ============== POINT DATA =============

    point_size = 5.0
    point_sensitivity_size = 9.0

    # ============== BEZIER CURVE OPTIONS ================
    curve_autoclose_flag = 0

    curve_stroke_color = (0.0, 0.0, 0.0)
    curve_stroke_width = 0.7
    curve_trace_color = (1.0, 0.0, 0.0)
    curve_point_sensitivity_size = 12.0

    curve_start_point_size = 5.0
    curve_start_point_fill = (1.0, 1.0, 1.0)
    curve_start_point_stroke = (0.0, 0.0, 0.0)
    curve_start_point_stroke_width = 2.0

    curve_point_size = 5.0
    curve_point_fill = (1.0, 1.0, 1.0)
    curve_point_stroke = (0.0, 0.3, 1.0)
    curve_point_stroke_width = 1.0

    curve_last_point_size = 5.0
    curve_last_point_fill = (1.0, 1.0, 1.0)
    curve_last_point_stroke = (0.0, 0.3, 1.0)
    curve_last_point_stroke_width = 2.0

    control_point_size = 5.0
    control_point_fill = (1.0, 1.0, 1.0)
    control_point_stroke = (0.0, 0.0, 0.0)
    control_point_stroke_width = 1.0

    control_line_stroke_color = (0.0, 0.5, 0.0)
    control_line_bg_stroke_color = (1.0, 1.0, 1.0)
    control_line_stroke_width = 0.7
    control_line_stroke_dash = [5, 5]

    selected_node_fill = (1.0, 0.5, 0.5)

    curve_new_point_size = 7.0
    curve_new_point_fill = (0.78, 1.0, 0.78)
    curve_new_point_stroke = (0.2, 0.59, 0.2)
    curve_new_point_stroke_width = 1.0

    # ============== RECT OPTIONS ================

    rect_midpoint_size = 5.0
    rect_midpoint_fill = (1.0, 0.97, 0.86)
    rect_midpoint_stroke = (1.0, 0.8, 0.2)
    rect_midpoint_stroke_width = 1.0

    rect_point_size = 5.0
    rect_point_fill = (1.0, 1.0, 1.0)
    rect_point_stroke = (0.0, 0.3, 1.0)
    rect_point_stroke_width = 1.0

    # ============== ELLIPSE OPTIONS ================

    ellipse_start_point_size = 5.0
    ellipse_start_point_fill = (1.0, 1.0, 1.0)
    ellipse_start_point_stroke = (0.0, 0.3, 1.0)
    ellipse_start_point_stroke_width = 2.0

    ellipse_end_point_size = 5.0
    ellipse_end_point_fill = (1.0, 1.0, 1.0)
    ellipse_end_point_stroke = (0.0, 0.0, 0.0)
    ellipse_end_point_stroke_width = 2.0

    ellipse_fixed_angle = 15.0

    # ============== POLYGON OPTIONS ================

    polygon_point_size = 5.0
    polygon_point_fill = (1.0, 1.0, 1.0)
    polygon_point_stroke = (0.0, 0.3, 1.0)
    polygon_point_stroke_width = 1.0

    # ============== TEXT OPTIONS ================

    text_point_size = 5.0
    text_point_fill = (1.0, 1.0, 1.0)
    text_point_stroke = (0.0, 0.3, 1.0)
    text_point_stroke_width = 1.0

    text_selected_point_fill = (1.0, 0.5, 0.5)

    # ============== GRADIENT MARK OPTIONS ================

    gradient_vector_fg_color = (1.0, 0.0, 0.0)
    gradient_vector_bg_color = (1.0, 1.0, 1.0)
    gradient_vector_width = 1.0
    gradient_vector_dash = [5, 5]
    gradient_vector_point_size = 5.0
    gradient_vector_point_fill = (1.0, 1.0, 1.0)
    gradient_vector_point_stroke = (0.0, 0.3, 1.0)
    gradient_vector_point_stroke_width = 1.0

    # ============== TEXT MARK OPTIONS ================
    text_cursor_width = 1.0
    text_cursor_color = (1.0, 0.0, 0.0)
    text_selection_color = (.098, .6824, 1.0, .2392)

    # ============== FONT OPTIONS ================
    font_preview_text = 'Lorem ipsum dolor sit amet, consectetur adipisicing'
    font_preview_width = 400
    font_preview_size = 14
    font_preview_color = (0.7, 0.7, 0.7)

    # ===UNSORTED===
    default_polygon_num = 5

    def is_linux(self):
        return self.os == system.LINUX

    def is_ubuntu(self):
        return self.os_name == system.UBUNTU

    def is_mac(self):
        return self.os == system.MACOSX

    def is_win(self):
        return self.os == system.WINDOWS


class LinuxConfig(AppConfig):
    os = system.LINUX
    os_name = system.get_os_name()
    statusbar_fontsize = 9
    tabs_fontsize = 9
    tabs_use_bold = False


class MacosxConfig(AppConfig):
    os = system.MACOSX
    os_name = system.get_os_name()
    toolbar_size = (16, 16)
    toolbar_icon_size = (16, 16)
    spin_overlay = False


class WinConfig(AppConfig):
    os = system.WINDOWS
    os_name = system.get_os_name()
    toolbar_size = (24, 24)
    toolbar_icon_size = (22, 22)
    tabs_use_bold = False

    prefs_dlg_size = (700, 450)
    prefs_dlg_minsize = (700, 450)

    history_dlg_size = (630, 350)
    history_dlg_minsize = (630, 350)

    fill_dlg_size = (440, 395)
    stroke_dlg_size = (430, 395)


def get_app_config():
    os_mapping = {system.MACOSX: MacosxConfig, system.WINDOWS: WinConfig}
    return os_mapping.get(system.get_os_family(), LinuxConfig)()
