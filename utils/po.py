# -*- coding: utf-8 -*-
#
#   Localization utils
#
# 	Copyright (C) 2018 by Igor E. Novikov
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
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from . import fsutils


def build_pot(paths, po_file='messages.po', error_logs=False):
    ret = 0
    files = []
    error_logs = 'warnings.log' if error_logs else '/dev/null'
    file_list = 'locale.in'
    for path in paths:
        files += fsutils.get_files_tree(path, 'py')
    open(file_list, 'w').write('\n'.join(files))
    ret += os.system('xgettext -f %s -L Python -o %s 2>%s' %
                     (file_list, po_file, error_logs))
    ret += os.system('rm -f %s' % file_list)
    if not ret:
        print 'POT file updated'


def build_locales(src_path, dest_path, textdomain):
    print 'Building locales'
    for item in fsutils.get_filenames(src_path, 'po'):
        lang = item.split('.')[0]
        po_file = os.path.join(src_path, item)
        mo_dir = os.path.join(dest_path, lang, 'LC_MESSAGES')
        mo_file = os.path.join(mo_dir, textdomain + '.mo')
        if not os.path.lexists(mo_dir):
            os.makedirs(mo_dir)
        print po_file, '==>', mo_file
        os.system('msgfmt -o %s %s' % (mo_file, po_file))
