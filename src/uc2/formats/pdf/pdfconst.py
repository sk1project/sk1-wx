# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Igor E. Novikov
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


PDF_SIGNATURE = '%PDF-1'

PDF_1_4 = ((1, 4), '')
PDF_1_5 = ((1, 5), '')
PDF_1_6 = ((1, 6), '')
PDF_1_7 = ((1, 7), '')
PDF_X_4 = ((1, 4), 'PDF/X-4')

PDF_VERSION_DEFAULT = PDF_X_4

PDF_VERSIONS = (PDF_1_4, PDF_1_5, PDF_1_6, PDF_1_7, PDF_X_4)
PDF_VER_NAMES = ('PDF 1.4', 'PDF 1.5', 'PDF 1.6', 'PDF 1.7', 'PDF/X-4')
