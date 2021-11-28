# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013 by Ihor E. Novikov
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

from wal import error_dialog, msg_dialog, stop_dialog, yesno_dialog, ync_dialog

from .aboutdlg import about_dialog
from .docinfodlg import docinfo_dlg
from .docprops import docprops_dlg
from .editdlg import edit_dlg, multiline_edit_dlg
from .filedlgs import get_dir_path, get_open_file_name, get_save_file_name
from .filelogviewer import filelog_viewer_dlg
from .filldlg import fill_dlg
from .logconsole import logconsole_dlg
from .pagedlg import delete_page_dlg, goto_page_dlg, insert_page_dlg
from .palcoldlg import palette_collection_dlg
from .paletteinfo import palette_info_dlg
from .progressdlg import ProgressDialog
from .strokedlg import stroke_dlg
