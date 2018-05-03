# -*- coding: utf-8 -*-
#
#   Setup utils module
#
# 	Copyright (C) 2013-2016 by Igor E. Novikov
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

import commands
import os
import platform
import shutil
import string
import sys


############################################################
#
# File system routines
#
############################################################

def get_dirs(path='.'):
    """
    Return directory list for provided path
    """
    result = []
    names = []
    if path:
        if os.path.isdir(path):
            try:
                names = os.listdir(path)
            except os.error:
                return []
        names.sort()
        for name in names:
            if os.path.isdir(os.path.join(path, name)):
                result.append(name)
        return result


def get_dirs_withpath(path='.'):
    """
    Return full  directory names list for provided path
    """
    result = []
    names = []
    if os.path.isdir(path):
        try:
            names = os.listdir(path)
        except os.error:
            return names
    names.sort()
    for name in names:
        if os.path.isdir(os.path.join(path, name)) and not name == '.svn':
            result.append(os.path.join(path, name))
    return result


def get_files(path='.', ext='*'):
    """
    Returns file list for provided path
    """
    result = []
    names = []
    if path:
        if os.path.isdir(path):
            try:
                names = os.listdir(path)
            except os.error:
                return []
        names.sort()
        for name in names:
            if not os.path.isdir(os.path.join(path, name)):
                if ext == '*':
                    result.append(name)
                elif '.' + ext == name[-1 * (len(ext) + 1):]:
                    result.append(name)
    return result


def get_files_withpath(path='.', ext='*'):
    """
    Returns full file names list for provided path
    """
    import glob
    file_items = glob.glob(os.path.join(path, "*." + ext))
    file_items.sort()
    result = []
    for file_item in file_items:
        if os.path.isfile(file_item):
            result.append(file_item)
    return result


def get_dirs_tree(path='.'):
    """
    Returns recursive directories list for provided path
    """
    tree = get_dirs_withpath(path)
    res = [] + tree
    for node in tree:
        subtree = get_dirs_tree(node)
        res += subtree
    return res


def get_files_tree(path='.', ext='*'):
    """
    Returns recursive files list for provided path
    """
    tree = []
    dirs = [path, ]
    dirs += get_dirs_tree(path)
    for dir_item in dirs:
        files = get_files_withpath(dir_item, ext)
        files.sort()
        tree += files
    return tree


def generate_locales():
    """
    Generates *.mo files Resources/Messages
    """
    print 'LOCALES BUILD'
    files = get_files('po', 'po')
    if len(files):
        for file_item in files:
            lang = file_item.split('.')[0]
            po_file = os.path.join('po', file_item)
            mo_file = os.path.join(
                'src', 'Resources', 'Messages', lang,
                'LC_MESSAGES', 'skencil.mo')
            if not os.path.lexists(os.path.join(
                    'src', 'Resources', 'Messages', lang, 'LC_MESSAGES')):
                os.makedirs(os.path.join(
                    'src', 'share', 'Messages', lang, 'LC_MESSAGES'))
            print po_file, '==>', mo_file
            os.system('msgfmt -o ' + mo_file + ' ' + po_file)


############################################################
#
# Routines for setup build
#
############################################################

def get_resources(pkg_path, path):
    path = os.path.normpath(path)
    pkg_path = os.path.normpath(pkg_path)
    size = len(pkg_path) + 1
    dirs = get_dirs_tree(path)
    dirs.append(path)
    res_dirs = []
    for item in dirs:
        res_dirs.append(os.path.join(item[size:], '*.*'))
    return res_dirs


def clear_build():
    """
    Clears build result.
    """
    os.system('rm -f MANIFEST')
    os.system('rm -rf build')


def clear_msw_build():
    """
    Clears build result on MS Windows.
    """
    shutil.rmtree('build', True)


def make_source_list(path, file_list=None):
    """
    Returns list of paths for provided file list.
    """
    if file_list is None:
        file_list = []
    ret = []
    for item in file_list:
        ret.append(os.path.join(path, item))
    return ret


INIT_FILE = '__init__.py'


def is_package(path):
    """
    Checks is provided directory a python package.
    """
    if os.path.isdir(path):
        marker = os.path.join(path, INIT_FILE)
        if os.path.isfile(marker):
            return True
    return False


def get_packages(path):
    """
    Collects recursively python packages.
    """
    packages = []
    items = []
    if os.path.isdir(path):
        try:
            items = os.listdir(path)
        except os.error:
            pass
        for item in items:
            if item == '.svn':
                continue
            folder = os.path.join(path, item)
            if is_package(folder):
                packages.append(folder)
                packages += get_packages(folder)
    packages.sort()
    return packages


def get_package_dirs(path='src', excludes=None):
    """
    Collects root packages.
    """
    if excludes is None:
        excludes = []
    dirs = {}
    items = []
    if os.path.isdir(path):
        try:
            items = os.listdir(path)
        except os.error:
            pass
        for item in items:
            if item in excludes:
                continue
            if item == '.svn':
                continue
            folder = os.path.join(path, item)
            if is_package(folder):
                dirs[item] = folder
    return dirs


def get_source_structure(path='src', excludes=None):
    """
    Returns recursive list of python packages. 
    """
    if excludes is None:
        excludes = []
    pkgs = []
    for item in get_packages(path):
        res = item.replace('\\', '.').replace('/', '.').split('src.')[1]
        check = True
        for exclude in excludes:
            if len(res) >= len(exclude) and res[:len(exclude)] == exclude:
                check = False
                break
        if check:
            pkgs.append(res)
    return pkgs


def compile_sources():
    """
    Compiles python sources in build/ directory.
    """
    import compileall
    compileall.compile_dir('build')


def copy_modules(modules, src_root='src'):
    """
    Copies native modules into src/
    The routine implements build_update command
    functionality and executed after "setup.py build" command.
    """
    version = (string.split(sys.version)[0])[0:3]
    machine = platform.machine()
    ext = '.so'
    prefix = 'build/lib.linux-' + machine + '-' + version

    if os.name == 'nt' and platform.architecture()[0] == '32bit':
        prefix = 'build/lib.win32-' + version
        ext = '.pyd'
    elif os.name == 'nt' and platform.architecture()[0] == '64bit':
        prefix = 'build/lib.win-amd64-' + version
        ext = '.pyd'

    for item in modules:
        path = os.path.join(*item.name.split('.')) + ext
        src = os.path.join(prefix, path)
        dst = os.path.join(src_root, path)
        shutil.copy(src, dst)
        print '>>>Module %s has been copied to src/ directory' % path


############################################################
#
# --- DEB package builder
#
############################################################

def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


RM_CODE = 'REMOVING'
MK_CODE = 'CREATING'
CP_CODE = 'COPYING '
ER_CODE = 'ERROR'
INFO_CODE = ''


def info(msg, code=''):
    if code == ER_CODE:
        ret = '%s>>> %s' % (code, msg)
    elif not code:
        ret = msg
    else:
        ret = '%s: %s' % (code, msg)
    print ret


def _make_dir(path):
    if not os.path.lexists(path):
        info('%s directory.' % path, MK_CODE)
        try:
            os.makedirs(path)
        except:
            raise IOError('Error while creating %s directory.' % path)


def copy_scripts(folder, scripts):
    if not scripts:
        return
    _make_dir(folder)
    for item in scripts:
        info('%s -> %s' % (item, folder), CP_CODE)
        if os.system('cp %s %s' % (item, folder)):
            raise IOError('Cannot copying %s -> %s' % (item, folder))
        filename = os.path.basename(item)
        path = os.path.join(folder, filename)
        if os.path.isfile(path):
            info('%s as executable' % path, MK_CODE)
            if os.system('chmod +x %s' % path):
                raise IOError('Cannot set executable flag for %s' % path)


def copy_files(path, files):
    if files and not os.path.isdir(path):
        _make_dir(path)
    if not files:
        return
    for item in files:
        msg = '%s -> %s' % (item, path)
        if len(msg) > 80:
            msg = '%s -> \n%s%s' % (item, ' ' * 10, path)
        info(msg, CP_CODE)
        if os.system('cp %s %s' % (item, path)):
            raise IOError('Cannot copying %s -> %s' % (item, path))


class DebBuilder:
    """
    Represents deb package build object.
    The object implements "setup.py bdist_deb" command.
    Works after regular "setup.py build" command and 
    constructs deb package using build result in build/ directory.
    Arguments:
    
    name - package names
    version - package version
    arch - system architecture (amd64, i386, all), if not provided will be
            detected automatically
    maintainer - package maintainer (John Smith <js@email.x>)
    depends - comma separated string of dependencies
    section - package section (default 'python')
    priority - package priority for users (default 'optional')
    homepage - project homepage
    description - short package description
    long_description - long description as defined by Debian rules
    package_dirs - list of root python packages
    scripts - list of executable scripts
    data_files - list of data files and appropriate destination directories. 
    deb_scripts - list of Debian package scripts.
    """

    name = None
    package_dirs = {}
    package_data = {}
    scripts = []
    data_files = []
    deb_scripts = []

    package = ''
    version = None
    arch = ''
    maintainer = ''
    installed_size = 0
    depends = ''
    section = 'python'
    priority = 'optional'
    homepage = ''
    description = ''
    long_description = ''

    package_name = ''
    py_version = ''
    machine = ''
    build_dir = 'build/deb-root'
    deb_dir = 'build/deb-root/DEBIAN'
    src = ''
    dst = ''
    bin_dir = ''
    pixmaps_dir = ''
    apps_dir = ''

    def __init__(
            self,
            name='',
            version='',
            arch='',
            maintainer='',
            depends='',
            section='',
            priority='',
            homepage='',
            description='',
            long_description='',
            package_dirs=None,
            package_data=None,
            scripts=None,
            data_files=None,
            deb_scripts=None,
            dst=''):

        if deb_scripts is None:
            deb_scripts = []
        if data_files is None:
            data_files = []
        if scripts is None:
            scripts = []
        if package_dirs is None:
            package_dirs = []
        if package_data is None:
            package_data = {}

        self.name = name
        self.version = version
        self.arch = arch
        self.maintainer = maintainer
        self.depends = depends
        if section:
            self.section = section
        if priority:
            self.priority = priority
        self.homepage = homepage
        self.description = description
        self.long_description = long_description

        self.package_dirs = package_dirs
        self.package_data = package_data
        self.scripts = scripts
        self.data_files = data_files
        self.deb_scripts = deb_scripts
        if dst:
            self.dst = dst

        self.package = 'python-%s' % self.name
        self.py_version = (string.split(sys.version)[0])[0:3]

        if not self.arch:
            arch = platform.architecture()[0]
            if arch == '64bit':
                self.arch = 'amd64'
            else:
                self.arch = 'i386'

        self.machine = platform.machine()

        self.src = 'build/lib.linux-%s-%s' % (self.machine, self.py_version)

        if not self.dst:
            path = '%s/usr/lib/python%s/dist-packages'
            self.dst = path % (self.build_dir, self.py_version)
        else:
            self.dst = self.build_dir + self.dst
        self.bin_dir = '%s/usr/bin' % self.build_dir

        self.package_name = 'python-%s-%s_%s.deb' % (
            self.name, self.version, self.arch)
        self.build()

    def clear_build(self):
        if os.path.lexists(self.build_dir):
            info('%s directory.' % self.build_dir, RM_CODE)
            if os.system('rm -rf ' + self.build_dir):
                raise IOError(
                    'Error while removing %s directory.' % self.build_dir)
        if os.path.lexists('dist'):
            info('Cleaning dist/ directory.', RM_CODE)
            if os.system('rm -rf dist/*.deb'):
                raise IOError('Error while cleaning dist/ directory.')
        else:
            _make_dir('dist')

    def write_control(self):
        _make_dir(self.deb_dir)
        control_list = [
            ['Package', self.package],
            ['Version', self.version],
            ['Architecture', self.arch],
            ['Maintainer', self.maintainer],
            ['Installed-Size', self.installed_size],
            ['Depends', self.depends],
            ['Section', self.section],
            ['Priority', self.priority],
            ['Homepage', self.homepage],
            ['Description', self.description],
            ['', self.long_description],
        ]
        path = os.path.join(self.deb_dir, 'control')
        info('Writing Debian control file.', MK_CODE)
        try:
            control = open(path, 'w')
            for item in control_list:
                name, val = item
                if val:
                    if name:
                        control.write('%s: %s\n' % (name, val))
                    else:
                        control.write('%s\n' % val)
            control.close()
        except:
            raise IOError('Error while writing Debian control file.')

    def copy_build(self):
        for item in os.listdir(self.src):
            path = os.path.join(self.src, item)
            if os.path.isdir(path):
                info('%s -> %s' % (path, self.dst), CP_CODE)
                if os.system('cp -R %s %s' % (path, self.dst)):
                    raise IOError(
                        'Error while copying %s -> %s' % (path, self.dst))
            elif os.path.isfile(path):
                info('%s -> %s' % (path, self.dst), CP_CODE)
                if os.system('cp %s %s' % (path, self.dst)):
                    raise IOError(
                        'Error while copying %s -> %s' % (path, self.dst))

    def copy_data_files(self):
        for item in self.data_files:
            path, files = item
            copy_files(self.build_dir + path, files)

    def copy_package_data_files(self):
        files = []
        pkgs = self.package_data.keys()
        for pkg in pkgs:
            items = self.package_data[pkg]
            for item in items:
                path = os.path.join(self.package_dirs[pkg], item)
                if os.path.basename(path) == '*.*':
                    flist = []
                    folder = os.path.join(self.dst, os.path.dirname(item))
                    fldir = os.path.dirname(path)
                    fls = os.listdir(fldir)
                    for fl in fls:
                        flpath = os.path.join(fldir, fl)
                        if os.path.isfile(flpath):
                            flist.append(flpath)
                    files.append([folder, flist])
                else:
                    if os.path.isfile(path):
                        folder = os.path.join(self.dst, os.path.dirname(item))
                        files.append([folder, [path, ]])
        for item in files:
            path, files = item
            copy_files(path, files)

    def make_package(self):
        os.system('chmod -R 755 %s' % self.build_dir)
        info('%s package.' % self.package_name, MK_CODE)
        if os.system('sudo dpkg --build %s/ dist/%s' % (
                self.build_dir, self.package_name)):
            raise IOError('Cannot create package %s' % self.package_name)

    def build(self):
        line = '=' * 30
        info(line + '\n' + 'DEB PACKAGE BUILD' + '\n' + line)
        try:
            if not os.path.isdir('build'):
                raise IOError('There is no project build! '
                              'Run "setup.py build" and try again.')
            self.clear_build()
            _make_dir(self.dst)
            self.copy_build()
            copy_scripts(self.bin_dir, self.scripts)
            copy_scripts(self.deb_dir, self.deb_scripts)
            self.copy_data_files()
            self.installed_size = str(int(get_size(self.build_dir) / 1024))
            self.write_control()
            self.make_package()
        except IOError as e:
            info(e, ER_CODE)
            info(line + '\n' + 'BUILD FAILED!')
            return 1
        info(line + '\n' + 'BUILD SUCCESSFUL!')
        return 0


class RpmBuilder:
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

        if data_files is None:
            data_files = []
        if not release:
            release = '0'

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
            '%files',
                      '%{_bindir}/' + self.name,
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


def build_pot(paths, po_file='messages.po', error_logs=False):
    ret = 0
    files = []
    error_logs = 'warnings.log' if error_logs else '/dev/null'
    file_list = 'locale.in'
    for path in paths:
        files += get_files_tree(path, 'py')
    open(file_list, 'w').write('\n'.join(files))
    ret += os.system('xgettext -f %s -L Python -o %s 2>%s' %
                     (file_list, po_file, error_logs))
    ret += os.system('rm -f %s' % file_list)
    if not ret:
        print 'POT file updated'


def build_locales(src_path, dest_path, textdomain):
    print 'Building locales'
    for item in get_files(src_path, 'po'):
        lang = item.split('.')[0]
        po_file = os.path.join(src_path, item)
        mo_dir = os.path.join(dest_path, lang, 'LC_MESSAGES')
        mo_file = os.path.join(mo_dir, textdomain + '.mo')
        if not os.path.lexists(mo_dir):
            os.makedirs(mo_dir)
        print po_file, '==>', mo_file
        os.system('msgfmt -o %s %s' % (mo_file, po_file))
