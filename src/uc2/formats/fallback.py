# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2015 by Igor E. Novikov
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

from uc2 import libimg
from uc2 import uc2const, sk2const
from uc2.formats.sk2 import sk2_model
from uc2.formats.sk2.sk2_presenter import SK2_Presenter
from uc2.utils.fsutils import get_fileptr
from uc2.utils.mixutils import merge_cnf


def im_loader(appdata, filename=None, fileptr=None, translate=True, cnf=None,
              **kw):
    cnf = merge_cnf(cnf, kw)

    sk2_doc = SK2_Presenter(appdata, cnf)
    sk2_doc.doc_file = filename
    sk2_doc.methods.set_doc_origin(sk2const.DOC_ORIGIN_LU)
    sk2_doc.methods.set_doc_units(uc2const.UNIT_PX)
    page = sk2_doc.methods.get_page()

    image_obj = sk2_model.Pixmap(sk2_doc.config)
    image_obj.handler.load_from_file(sk2_doc.cms, filename)

    orient = uc2const.PORTRAIT
    w = image_obj.size[0] * uc2const.px_to_pt
    h = image_obj.size[1] * uc2const.px_to_pt
    if image_obj.size[0] > image_obj.size[1]:
        orient = uc2const.LANDSCAPE

    image_obj.trafo = [1.0, 0.0, 0.0, 1.0, -w / 2.0, -h / 2.0]

    sk2_doc.methods.set_page_format(page, ['Custom', (w, h), orient])
    sk2_doc.methods.set_default_page_format(['Custom', (w, h), orient])
    grid_layer = sk2_doc.methods.get_grid_layer()
    grid_layer.grid = [0, 0, uc2const.px_to_pt, uc2const.px_to_pt]
    grid_layer.properties = [1, 0, 0]

    layer = sk2_doc.methods.get_layer(page)

    layer.childs.append(image_obj)
    sk2_doc.update()
    return sk2_doc


def fallback_check(path):
    return libimg.check_image(path)
