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

import os

from uc2.formats.generic_filters import AbstractSaver

import pdfgen


class PDF_Saver(AbstractSaver):
    name = 'PDF_Saver'

    def do_save(self):
        renderer = pdfgen.PDFGenerator(self.fileptr, self.presenter.cms)

        # ---PDF doc data
        appdata = self.presenter.appdata
        creator = '%s %s' % (appdata.app_name, appdata.version)
        producer = '%s %s' % ('UniConvertor', appdata.version)
        metainfo = self.presenter.model.metainfo
        subject = '---'
        author = ''
        keywords = ''
        title = ''
        if metainfo:
            author = metainfo[0]
            keywords = metainfo[2]
        if self.filepath:
            title = os.path.basename(self.filepath)
            title = os.path.splitext(title)[0]

        renderer.set_creator(creator)
        renderer.set_producer(producer)
        renderer.set_title(title)
        renderer.set_author(author)
        renderer.set_subject(subject)
        renderer.set_keywords(keywords)
        # ---PDF doc data end

        renderer.set_compression(True)

        methods = self.presenter.methods
        desktop_layers = methods.get_desktop_layers()
        master_layers = methods.get_master_layers()
        pages = methods.get_pages()

        renderer.set_num_pages(len(pages))

        for page in pages:
            w, h = methods.get_page_size(page)
            renderer.start_page(w, h)

            layers = desktop_layers + methods.get_layers(page)
            layers += master_layers
            for layer in layers:
                if methods.is_layer_visible(layer):
                    renderer.render(layer.childs, True)
            renderer.end_page()
        renderer.save()
