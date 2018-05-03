# -*- coding: utf-8 -*-
#
#   RPM builder
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


class RpmBuilder(object):
    """
    Represents rpm package build object.
    The object implements "setup.py bdist_rpm" command.
    Works after regular "setup.py build" command and
    constructs rpm package using build result of "setup.py sdist".
    Arguments:

    name - package names
    version - package version
    release - release marker
    arch - system architecture (i686, x86_64), if not provided will be
            detected automatically
    maintainer - package maintainer (John Smith <js@email.x>)
    summary - short package description
    description - long description as defined by Debian rules
    license - project license
    url - project homepage
    depends - list of dependencies

    build_cmd - command to build project
    install_dir - installation path
    data_files - list of data files and appropriate destination directories.
    """

    def __init__(
            self,
            name='',
            version='',
            release='',
            arch='',
            maintainer='',
            summary='',
            description='',
            license='',
            url='',
            depends='',

            build_script='',
            install_path='',
            data_files=None,
    ):

        data_files = data_files or []
        release = release or '0'

        self.name = name
        self.version = version
        self.release = release
        self.arch = arch
        self.maintainer = maintainer
        self.summary = summary
        self.description = description
        self.license = license
        self.url = url
        self.depends = depends
        self.build_script = build_script
        self.install_path = install_path
        self.data_files = data_files

        self.current_path = os.path.abspath('.')
        self.rpmbuild_path = os.path.expanduser('~/rpmbuild')
        self.spec_path = os.path.join(self.rpmbuild_path,
                                      'SPECS', '%s.spec' % self.name)
        self.dist_dir = os.path.join(self.current_path, 'dist')
        self.tarball = ''

        self.clear_rpmbuild()
        self.create_rpmbuild()
        self.copy_sources(*self.find_tarball())
        self.write_spec()
        os.chdir(self.rpmbuild_path + '/SPECS')
        self.build_rpm()
        self.clear_rpmbuild()

    def find_tarball(self):
        if not os.path.exists(self.dist_dir):
            raise IOError('There is no ./dist source folder!')
        file_items = os.listdir(self.dist_dir)
        for item in file_items:
            file_path = os.path.join(self.dist_dir, item)
            if os.path.isfile(file_path) and file_path.endswith('.tar.gz'):
                return file_path, item
        raise IOError('There is no source tarball in ./dist folder!')

    def create_rpmbuild(self):
        for item in ('', 'BUILD', 'BUILDROOT', 'SOURCES',
                     'SPECS', 'RPMS', 'SRPMS'):
            os.mkdir('%s/%s' % (self.rpmbuild_path, item))

    def copy_sources(self, file_path, file_name):
        self.tarball = self.rpmbuild_path + '/SOURCES/' + file_name
        os.system('cp %s %s' % (file_path, self.tarball))
        os.remove(file_path)

    def write_spec(self):
        content = [
            'Name: %s' % self.name,
            'Version: %s' % self.version,
            'Release: %s' % self.release,
            'Summary: %s' % self.summary,
            '',
            'License: %s' % self.license,
            'URL: %s' % self.url,
            'Source: %s' % self.tarball,
            '']
        for item in self.depends:
            content.append('Requires: %s' % item)
        content += [
            '',
            '%description', self.description,
            '',
            '%prep', '%autosetup -n {}-{}'.format(self.name, self.version),
            '',
            '%build', '/usr/bin/python2 %s build' % self.build_script,
            '',
            '%install',
            'rm -rf $RPM_BUILD_ROOT',
            '/usr/bin/python2 %s install --root=$RPM_BUILD_ROOT' % self.build_script,
            '',
            '%files', '%{_bindir}/' + self.name,
            self.install_path.replace('/usr/', '%{_usr}/'),
        ]
        for item in self.data_files:
            if item[0].startswith('/usr/share/'):
                path = item[0].replace('/usr/share/', '%{_datadir}/')
                for filename in item[1]:
                    content.append('%s/%s' % (path, filename.split('/')[-1]))
        content += ['', ]

        open(self.spec_path, 'w').write('\n'.join(content))

    def build_rpm(self):
        os.system('rpmbuild -bb %s --define "_topdir %s"' % (self.spec_path,
                                                             self.rpmbuild_path))
        os.system('cp `find %s -name "*.rpm"` %s/' % (self.rpmbuild_path,
                                                      self.dist_dir))

    def clear_rpmbuild(self):
        if os.path.exists(self.rpmbuild_path):
            os.system('rm -rf %s' % self.rpmbuild_path)
