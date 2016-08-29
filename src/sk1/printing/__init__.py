# -*- coding: utf-8 -*-
#
#	Copyright (C) 2016 by Igor E. Novikov
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

import wal

from sk1 import _
from sk1.dialogs import ProgressDialog, error_dialog

from printdlg import PrintDialog
from printout import Printout

def print_dlg(parent, presenter):
	app = presenter.app
	if wal.is_msw():
		return
	else:
		from cups_staff import CUPS_PS
		printsys = CUPS_PS()

	printout = Printout(presenter)
	dlg = PrintDialog(parent, printsys, printout)
	printer = dlg.show()

	if printer:
		pd = ProgressDialog(_('Printing...'), parent)
		ret = pd.run(printer.printing, [printout, ], save_result=False)
		pd.destroy()
		if not ret:
			msg = _('Error while printing!')
			error_dialog(parent, app.appdata.app_name, msg)
