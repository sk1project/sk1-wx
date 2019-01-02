# -*- coding: utf-8 -*-
#
#  Copyright (C) 2011-2013 by Igor E. Novikov
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

import os, shutil

from uc2.utils import generate_id
from uc2.utils.system import WINDOWS, get_os_family
from uc2.formats.pdxf import const

OS_FAMILY = get_os_family()


def convert_resource_path(path):
    if OS_FAMILY == WINDOWS:
        path = path.replace('/', '\\')
    return path


class ResourceManager:
    """
    Represents resource manager object to
    manage files included into PDXF file archive. 
    """

    def __init__(self, presenter):
        self.presenter = presenter
        self.doc_dir = presenter.doc_dir

    def get_resource_path(self, id):
        """
        Returns absolute path of resource file by id.
        If requested id is not in resources or resource file is
        absent, returns None. 
        """
        ret = None
        res_dict = self.presenter.model.resources
        if id in res_dict.keys():
            respath = convert_resource_path(res_dict[id])
            path = os.path.join(self.doc_dir, respath)
            if os.path.isfile(path):
                ret = path
        return ret

    def get_resources(self):
        """
        Returns id list and correspondent relative resource path list.
        If there aren't resources, returns two empty lists.
        """
        res_dict = self.presenter.model.resources
        ids = res_dict.keys()
        paths = []
        for item in ids:
            paths.append(res_dict[item])
        return ids, paths

    def get_resource(self, id):
        """
        Returns relative resource path by id.
        If there is no path for id, returns None.
        """
        ret = None
        res_dict = self.presenter.model.resources
        if id in res_dict.keys():
            ret = res_dict[id]
        return ret

    def copy_resources(self, rm, resources=[]):
        """
        Copies resources from other resource manager storing the same id.
        resources - list of ids
        """
        for id in resources:
            self.copy_resource(rm, id)

    def copy_resource(self, rm, id):
        """
        Copies resource from other resource manager by id.
        The id is storing. If wrong id or there is no resource file
        doesn't copy anything. 
        """
        filepath = rm.get_resource_path(id)
        if not filepath is None and os.path.isfile(filepath):
            place = rm.get_resource(id).split('/')[0]
            self.registry_file(filepath, place, id)

    def delete_resources(self, resources=[], rmfile=False):
        """
        Removes list of ids from resources.
        If rmfile flag is true removes files physically.
        resources - list of ids
        """
        for id in resources:
            self.delete_resource(id, rmfile)

    def delete_resource(self, id, rmfile=False):
        """
        Removes id from resources.
        If rmfile flag is true removes file physically.
        """
        res_dict = self.presenter.model.resources
        filepath = self.get_resource_path(id)
        if id in res_dict.keys():
            res_dict.pop(id)
            if rmfile and not filepath is None:
                try:
                    os.remove(filepath)
                except:
                    pass

    def registry_file(self, filepath, place, id=None):
        """
        Copies and registers file into specified place
        (one of document structure directories).
        If id is not provided, generates new unique id.
        """
        ret = None
        if os.path.isfile(filepath):
            if id is None:
                id = generate_id()
            filename = os.path.basename(filepath)
            ext = os.path.splitext(filename)[1]
            dst_filename = id + ext
            dst_dir = os.path.join(self.doc_dir, place)
            dst = os.path.join(dst_dir, dst_filename)
            try:
                shutil.copyfile(filepath, dst)
                res_dict = self.presenter.model.resources
                res_dict[id] = place + '/' + dst_filename
                ret = id
            except:
                pass
        return ret

    def registry_profile(self, filepath, id=None):
        """
        Copies and registers file into Profiles directory.
        If id is not provided, generates new unique id.
        """
        return self.registry_file(filepath, const.DOC_PROFILE_DIR, id)

    def registry_image(self, filepath, id=None):
        """
        Copies and registers file into Images directory.
        If id is not provided, generates new unique id.
        """
        return self.registry_file(filepath, const.DOC_IMAGE_DIR, id)

    def registry_preview(self, filepath, id=None):
        """
        Copies and registers file into Previews directory.
        If id is not provided, generates new unique id.
        """
        return self.registry_file(filepath, const.DOC_PREVIEW_DIR, id)

# if __name__ == '__main__':
#	print OS_FAMILY
#	print convert_resource_path('Image/test.png')
