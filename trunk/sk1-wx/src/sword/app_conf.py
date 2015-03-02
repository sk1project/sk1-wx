# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011 by Igor E. Novikov
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

from uc2.uc_conf import UCConfig, UCData
from uc2.utils import system
from uc2.utils.fs import expanduser_unicode

from sword import events

class AppData(UCData):

	app_name = 'SWord'
	app_proc = 'sword'
	app_org = 'sK1 Project'
	app_domain = 'sk1project.org'
	app_icon = None
	doc_icon = None
	version = "1.0"

	app_config_dir = expanduser_unicode(os.path.join('~', '.config', 's-word'))
	app_temp_dir = os.path.join(app_config_dir, 'temp')

	def __init__(self, app):

		UCData.__init__(self, app)

		if not os.path.lexists(self.app_temp_dir):
			os.makedirs(self.app_temp_dir)



class AppConfig(UCConfig):

	def __setattr__(self, attr, value):
		if not hasattr(self, attr) or getattr(self, attr) != value:
			self.__dict__[attr] = value
			events.emit(events.CONFIG_MODIFIED, attr, value)

	#============== GENERIC SECTION ===================
	system_encoding = 'utf-8'# default encoding (GUI uses utf-8 only)

	#============== EXTERNAL TOOLS ==================

	ext_image_view = 'eog $file'
	ext_text_view = 'kwrite $file'
	ext_doc_view = 'evince $file'
	ext_html_view = 'konqueror $file'
	ext_binary_view = 'okteta $file'
	ext_compare_view = 'kompare $file1 $file2'

	pseudomime = {
	'jpg':ext_image_view, 'jpeg':ext_image_view, 'tif':ext_image_view,
	'tiff':ext_image_view, 'bmp':ext_image_view, 'png':ext_image_view,
	'gif':ext_image_view,
	'pdf':ext_doc_view, 'ps':ext_doc_view,
	}

	#============== TOOLS SECTION ===================

	fb_show_hidden_files = 0
	fb_current_directory = ''
	fb_show_all_files = 1

	log_start_record = 1

	scr_show_hidden_files = 0
	scr_current_directory = ''
	scr_show_all_files = 0
	#============== UI SECTION ===================
	palette_cell_vertical = 18
	palette_cell_horizontal = 40
	palette_orientation = 1

	# 0 - tabbed
	# 1 - windowed
	interface_type = 0

	mw_maximized = 0

	mw_width = 1134
	mw_height = 700

	mw_min_width = 1134
	mw_min_height = 700

	show_splash = 1

	set_doc_icon = 1

	ruler_style = 1
	ruler_min_tick_step = 3
	ruler_min_text_step = 50
	ruler_max_text_step = 100

	# 0 - page center
	# 1 - lower-left page corner
	# 2 - upper-left page corner
	ruler_coordinates = 1

	# 'pt', 'in', 'cm', 'mm'
	default_unit = 'mm'

	sel_frame_offset = 10.0
	sel_frame_color = (0.0, 0.0, 0.0)
	sel_frame_dash = [5, 5]

	sel_marker_size = 9.0
	sel_marker_frame_color = (0.62745, 0.62745, 0.64314)
	sel_marker_frame_dash = [5, 5]
	sel_marker_fill = (1.0, 1.0, 1.0)
	sel_marker_stroke = (0.0, 0.3, 1.0)

	rotation_step = 5.0#in graduses
	stroke_sensitive_size = 5.0#in pixels

	#============== I/O SECTION ===================
	open_dir = '~'
	save_dir = '~'
	import_dir = '~'
	export_dir = '~'
	make_backup = 1
	resource_dir = ''

	def __init__(self, path):
		pass
#		self.resource_dir = os.path.join(path, 'share')




class LinuxConfig(AppConfig):
	os = system.LINUX

class MacosxConfig(AppConfig):
	os = system.MACOSX
	mw_maximized = 0
	set_doc_icon = 0
	ruler_style = 0

class WinConfig(AppConfig):
	os = system.WINDOWS
	ruler_style = 0



def get_app_config(path):
	os_family = system.get_os_family()
	if os_family == system.MACOSX:
		return MacosxConfig(path)
	elif os_family == system.WINDOWS:
		return WinConfig(path)
	else:
		return LinuxConfig(path)
