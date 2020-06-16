#!/usr/bin/env python2
#
#   BuildBox for sK1/UniConvertor 2.x
#
# 	Copyright (C) 2018 by Ihor E. Novikov
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

"""
Usage:
--------------------------------------------------------------------------
 to pull docker images:        python bbox.py pull
 to remove docker images:      python bbox.py rmi
 to run build for all images:  python bbox.py build
 to build package:             python bbox.py
--------------------------------------------------------------------------
BuildBox is designed to be used alongside Docker. To prepare environment
on Linux OS you need installing Docker. After that initialize
environment from sk1-wx project folder:

>sudo -s
>python bbox.py pull

To run build, just launch BuildBox:

>python bbox.py build
--------------------------------------------------------------------------
"""

import os
import shutil
import sys
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile

from utils import bbox, build
from utils.bbox import is_path, command, echo_msg, SYSFACTS, TIMESTAMP
from utils.fsutils import get_files_tree

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CURRENT_PATH, 'src'))

import sk1.appconst

# options processing
ARGV = {item.split('=')[0][2:]: item.split('=')[1]
        for item in sys.argv if item.startswith('--') and '=' in item}

# Output colors
STDOUT_MAGENTA = '\033[95m'
STDOUT_BLUE = '\033[94m'
STDOUT_GREEN = '\033[92m'
STDOUT_YELLOW = '\033[93m'
STDOUT_FAIL = '\033[91m'
STDOUT_ENDC = '\033[0m'
STDOUT_BOLD = '\033[1m'
STDOUT_UNDERLINE = '\033[4m'

SK1 = 'sk1'
PROJECT = SK1

# Build constants
IMAGE_PREFIX = 'sk1project/'
VAGRANT_DIR = '/vagrant'
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_DIR, 'src')
BUILD_DIR = os.path.join(PROJECT_DIR, 'build')
DIST_DIR = os.path.join(PROJECT_DIR, 'dist')
RELEASE_DIR = os.path.join(PROJECT_DIR, 'release')
PKGBUILD_DIR = os.path.join(PROJECT_DIR, 'pkgbuild')
ARCH_DIR = os.path.join(PROJECT_DIR, 'archlinux')
LOCALES_DIR = os.path.join(PROJECT_DIR, 'src/sk1/share/locales')
CACHE_DIR = os.path.join(PROJECT_DIR, 'subproj/build-cache')

SCRIPT = 'setup.py'
APP_NAME = SK1
APP_FULL_NAME = 'sK1'
APP_MAJOR_VER = sk1.appconst.VERSION
APP_REVISION = sk1.appconst.REVISION
APP_VER = '%s%s' % (APP_MAJOR_VER, APP_REVISION)

RELEASE = 'RELEASE' in os.environ or 'release' in ARGV
DEBUG_MODE = 'DEBUG_MODE' in os.environ
CONST_FILES = ['src/sk1/appconst.py',]


IMAGES = [
    'ubuntu_14.04_32bit',
    'ubuntu_14.04_64bit',
    'ubuntu_16.04_32bit',
    'ubuntu_16.04_64bit',
    'ubuntu_18.04_64bit',
    'ubuntu_18.10_64bit',
    'ubuntu_19.04_64bit',
    'ubuntu_19.10_64bit',
    'debian_8_32bit',
    'debian_8_64bit',
    'debian_9_32bit',
    'debian_9_64bit',
    'debian_10_32bit',
    'debian_10_64bit',
    'fedora_27_64bit',
    'fedora_28_64bit',
    'fedora_29_64bit',
    'fedora_30_64bit',
    'fedora_31_64bit',
    'opensuse_42.3_64bit',
    'opensuse_15.0_64bit',
    # 'opensuse_15.1_64bit',
    'packager'
]

LOCAL_IMAGES = [
    'ubuntu_16.04_64bit',
    # 'msw-packager',
]


def clear_folders():
    # Clear build folders
    if is_path(BUILD_DIR):
        command('rm -rf %s' % BUILD_DIR)
    if is_path(DIST_DIR):
        command('rm -rf %s' % DIST_DIR)
    if not is_path(RELEASE_DIR):
        os.makedirs(RELEASE_DIR)


def clear_files(folder, ext=None):
    ext = 'py' if ext is None else ext
    exts = [ext] if not isinstance(ext, list) else ext
    for ext in exts:
        for path in get_files_tree(folder, ext):
            if os.path.exists(path) and path.endswith(ext):
                os.remove(path)


def shell(cmd, times=1):
    for _i in range(times):
        if not os.system(cmd):
            return 0
    return 1


def set_build_stamp():
    if not RELEASE:
        for filename in CONST_FILES:
            with open(filename, 'rb') as fp:
                lines = fp.readlines()
            with open(filename, 'wb') as fp:
                marked = False
                for line in lines:
                    if not marked and line.startswith('BUILD = '):
                        line = 'BUILD = \'%s\'\n' % bbox.TIMESTAMP
                        marked = True
                    fp.write(line)


############################################################
# Main functions
############################################################


def pull_images():
    for image in IMAGES:
        msg = 'Pulling %s%s image' % (IMAGE_PREFIX, image)
        msg += ' ' * (50 - len(msg)) + '...'
        echo_msg(msg, newline=False)
        if shell('docker pull %s%s 1> /dev/null' % (IMAGE_PREFIX, image), 3):
            echo_msg('[ FAIL ]', code=STDOUT_FAIL)
            sys.exit(1)
        echo_msg('[  OK  ]', code=STDOUT_GREEN)


def remove_images():
    for image in IMAGES:
        command('docker rmi %s%s' % (IMAGE_PREFIX, image))


def rebuild_images():
    command('docker rm $(docker ps -a -q)  2> /dev/null')
    command('docker rmi $(docker images -a -q)  2> /dev/null')
    for image in IMAGES[:-1]:
        echo_msg('Rebuilding %s%s image' % (IMAGE_PREFIX, image),
                 code=STDOUT_MAGENTA)
        dockerfile = os.path.join(PROJECT_DIR, 'infra', 'bbox', 'docker', image)
        command('docker build -t %s%s %s' % (IMAGE_PREFIX, image, dockerfile))
        if not command('docker push %s%s' % (IMAGE_PREFIX, image)):
            command('docker rmi $(docker images -a -q)')


def run_build(locally=False, stop_on_error=True):
    echo_msg('Project %s build started' % PROJECT, code=STDOUT_MAGENTA)
    echo_msg('=' * 35, code=STDOUT_MAGENTA)
    if not locally:
        set_build_stamp()
    if is_path(RELEASE_DIR):
        command('sudo rm -rf %s' % RELEASE_DIR)
    if is_path(LOCALES_DIR):
        command('sudo rm -rf %s' % LOCALES_DIR)
    if PROJECT == SK1:
        command('cd %s && python setup.py build_locales' % PROJECT_DIR)
        echo_msg('=' * 35, code=STDOUT_MAGENTA)
    for image in IMAGES if not locally else LOCAL_IMAGES:
        os_name = image.capitalize().replace('_', ' ')
        msg = 'Build on %s' % os_name
        echo_msg(msg + ' ' * (35 - len(msg)) + '...', newline=False)
        output = ' 1> /dev/null 2> /dev/null' if not DEBUG_MODE else ''
        cmd = '/vagrant/bbox.py build_package --project=%s' % PROJECT
        if image == 'packager':
            cmd = '/vagrant/bbox.py packaging --project=%s' % PROJECT
        if RELEASE:
            cmd += ' --release=1'
        if shell('docker run --rm -v %s:%s %s%s %s %s' %
                 (PROJECT_DIR, VAGRANT_DIR,
                  IMAGE_PREFIX, image, cmd, output), 2):
            echo_msg('[ FAIL ]', code=STDOUT_FAIL)
            if stop_on_error or not locally:
                sys.exit(1)
        else:
            echo_msg('[  OK  ]', code=STDOUT_GREEN)
    if not locally:
        msg = 'Publishing result'
        msg = msg + ' ' * (35 - len(msg)) + '...'
        echo_msg(msg, newline=False)
        folder = PROJECT + '-release' if RELEASE else PROJECT
        if os.system('sshpass -e rsync -a --delete-after -e '
                     '\'ssh  -o StrictHostKeyChecking=no -o '
                     'UserKnownHostsFile=/dev/null -p 22\' '
                     './release/ `echo $RHOST`%s/ '
                     '1> /dev/null  2> /dev/null' % folder):
            echo_msg('[ FAIL ]', code=STDOUT_FAIL)
            sys.exit(1)
        echo_msg('[  OK  ]', code=STDOUT_GREEN)
    echo_msg('=' * 35, code=STDOUT_MAGENTA)


def run_build_local():
    run_build(locally=True, stop_on_error=False)
    command('chmod -R 777 %s' % RELEASE_DIR)
    command('sudo rm -rf %s' % LOCALES_DIR)


def build_package():
    mint_folder = os.path.join(RELEASE_DIR, 'LinuxMint')
    eos_folder = os.path.join(RELEASE_DIR, 'elementaryOS')
    mx_folder = os.path.join(RELEASE_DIR, 'MX_Linux')
    copies = []
    out = ' 1> /dev/null  2> /dev/null' if not DEBUG_MODE else ''

    clear_folders()

    if SYSFACTS.is_deb:
        echo_msg('Building DEB package')
        command('cd %s;python2 %s bdist_deb%s' % (PROJECT_DIR, SCRIPT, out))

        old_name = bbox.get_package_name(DIST_DIR)
        prefix, suffix = old_name.split('_')
        new_name = prefix + bbox.get_marker(not RELEASE) + suffix
        prefix += '_' + bbox.TIMESTAMP if not RELEASE else ''
        if SYSFACTS.is_ubuntu and SYSFACTS.version == '14.04':
            copies.append((prefix + '_mint_17_' + suffix, mint_folder))
            if SYSFACTS.is_64bit:
                copies.append((prefix + '_elementary0.3_' + suffix, eos_folder))
        elif SYSFACTS.is_ubuntu and SYSFACTS.version == '16.04':
            copies.append((prefix + '_mint_18_' + suffix, mint_folder))
            if SYSFACTS.is_64bit:
                copies.append((prefix + '_elementary0.4_' + suffix, eos_folder))
        elif SYSFACTS.is_ubuntu and SYSFACTS.version == '18.04':
            copies.append((prefix + '_mint_19_' + suffix, mint_folder))
            if SYSFACTS.is_64bit:
                copies.append((prefix + '_elementary5.0_' + suffix, eos_folder))
        elif SYSFACTS.is_debian:
            ver = SYSFACTS.version.split('.')[0]
            if ver == '8':
                copies.append((prefix + '_mx15_' + suffix, mx_folder))
                copies.append((prefix + '_mx16_' + suffix, mx_folder))
            elif ver == '9':
                copies.append((prefix + '_mx17_' + suffix, mx_folder))
                copies.append((prefix + '_mx18_' + suffix, mx_folder))
            elif ver == '10':
                copies.append((prefix + '_mx19_' + suffix, mx_folder))

    elif SYSFACTS.is_rpm:
        echo_msg('Building RPM package')
        command('cd %s;python2 %s bdist_rpm%s' % (PROJECT_DIR, SCRIPT, out))

        old_name = bbox.get_package_name(DIST_DIR)
        items = old_name.split('.')
        marker = bbox.get_marker(not RELEASE)
        new_name = '.'.join(items[:-2] + [marker, ] + items[-2:])
    else:
        echo_msg('Unsupported distro!', code=STDOUT_FAIL)
        sys.exit(1)

    distro_folder = os.path.join(RELEASE_DIR, SYSFACTS.hmarker)
    if not is_path(distro_folder):
        os.makedirs(distro_folder)
    old_name = os.path.join(DIST_DIR, old_name)
    package_name = os.path.join(RELEASE_DIR, distro_folder, new_name)
    command('cp %s %s' % (old_name, package_name))

    # Package copies
    for name, folder in copies:
        if not is_path(folder):
            os.makedirs(folder)
        name = os.path.join(RELEASE_DIR, folder, name)
        command('cp %s %s' % (old_name, name))

    if SYSFACTS.is_src:
        echo_msg('Creating source package')
        if os.path.isdir(DIST_DIR):
            shutil.rmtree(DIST_DIR, True)
        command('cd %s;python2 %s sdist %s' % (PROJECT_DIR, SCRIPT, out))
        old_name = bbox.get_package_name(DIST_DIR)
        marker = '_%s' % bbox.TIMESTAMP if not RELEASE else ''
        new_name = old_name.replace('.tar.gz', '%s.tar.gz' % marker)
        old_name = os.path.join(DIST_DIR, old_name)
        package_name = os.path.join(RELEASE_DIR, new_name)
        command('cp %s %s' % (old_name, package_name))

        # ArchLinux PKGBUILD
        if os.path.isdir(PKGBUILD_DIR):
            shutil.rmtree(PKGBUILD_DIR, True)
        os.mkdir(PKGBUILD_DIR)
        os.chdir(PKGBUILD_DIR)

        tarball = os.path.join(PKGBUILD_DIR, new_name)
        command('cp %s %s' % (package_name, tarball))

        dest = 'PKGBUILD'
        src = os.path.join(ARCH_DIR, '%s-%s' % (dest, APP_NAME))
        command('cp %s %s' % (src, dest))
        command("sed -i 's/VERSION/%s/g' %s" % (APP_VER, dest))
        command("sed -i 's/TARBALL/%s/g' %s" % (new_name, dest))

        dest = 'README'
        src = os.path.join(ARCH_DIR, '%s-%s' % (dest, APP_NAME))
        command('cp %s %s' % (src, dest))

        pkg_name = new_name.replace('.tar.gz', '.archlinux.pkgbuild.zip')
        arch_folder = os.path.join(RELEASE_DIR, 'ArchLinux')
        os.makedirs(arch_folder)
        pkg_name = os.path.join(arch_folder, pkg_name)
        ziph = ZipFile(pkg_name, 'w', ZIP_DEFLATED)
        for item in [new_name, 'PKGBUILD', 'README']:
            path = os.path.join(PKGBUILD_DIR, item)
            ziph.write(path, item)
        ziph.close()
        shutil.rmtree(PKGBUILD_DIR, True)

    clear_folders()


PKGS = ['sk1', 'uc2', 'wal']
EXTENSIONS = [
    'uc2/cms/_cms.pyd',
    'uc2/libcairo/_libcairo.pyd',
    'uc2/libimg/_libimg.pyd',
    'uc2/libpango/_libpango.pyd',
]

MSI_APP_VERSION = APP_MAJOR_VER if RELEASE \
    else '%s.%s %s' % (APP_MAJOR_VER, TIMESTAMP, APP_REVISION)

MSI_DATA = {
    # Required
    'Name': '%s %s' % (APP_FULL_NAME, APP_VER),
    'UpgradeCode': '3AC4B4FF-10C4-4B8F-81AD-BAC3238BF693',
    'Version': MSI_APP_VERSION,
    'Manufacturer': 'sK1 Project',
    # Optional
    'Description': '%s %s Installer' % (APP_FULL_NAME, APP_VER),
    'Comments': 'Licensed under GPL v3',
    'Keywords': 'Vector graphics, Prepress',

    # Structural elements
    '_Icon': os.path.join(CACHE_DIR, 'common/sk1.ico'),
    '_OsCondition': '601',
    '_SourceDir': '',
    '_InstallDir': '%s-%s' % (APP_FULL_NAME, APP_VER),
    '_OutputName': '',
    '_OutputDir': '',
    '_ProgramMenuFolder': 'sK1 Project',
    '_AddToPath': [''],
    '_Shortcuts': [
        {'Name': 'sK1 %s illustration program' % APP_VER,
         'Description': 'Open source sK1 vector graphics editor',
         'Target': 'sk1.exe',
         'AddOnDesktop': True,
         'Open': [],
         'OpenWith': ['.sk2', '.sk1', '.sk', '.svg', '.plt', '.wmf', '.fig',
                      '.cdr', '.cmx', '.cdt', '.ccx', '.xar', '.cgm',
                      # '.ai', '.ps', '.pdf', '.eps',
                      '.bmp', '.jpg', '.jpeg', '.j2p', '.png', '.tif', '.tiff',
                      '.gif', '.xcf', '.psd', '.pcx', '.xbm', '.xpm', '.ppm',
                      '.webp',
                      '.skp', '.gpl', '.xml', '.soc', '.ase', '.aco', '.cpl',
                      '.jcw']
         },
    ]
}


def packaging():
    build_msw_packages()


def build_msw_packages():
    import wixpy
    distro_folder = os.path.join(RELEASE_DIR, 'MS_Windows')

    for arch in ['win32', 'win64']:
        echo_msg('=== Arch %s ===' % arch)
        portable_name = '%s-%s-%s-portable' % (APP_NAME, APP_VER, arch)
        if not RELEASE:
            portable_name = '%s-%s-%s-%s-portable' % \
                            (APP_NAME, APP_VER, TIMESTAMP, arch)
        portable_folder = os.path.join(PROJECT_DIR, portable_name)
        portable_libs = os.path.join(portable_folder, 'libs')
        if os.path.exists(portable_folder):
            shutil.rmtree(portable_folder, True)
        os.mkdir(portable_folder)

        if not is_path(distro_folder):
            os.makedirs(distro_folder)

        # Package building
        echo_msg('Creating portable package')

        portable = os.path.join(CACHE_DIR,  arch, 'portable.zip')

        echo_msg('Extracting portable files from %s' % portable)
        ZipFile(portable, 'r').extractall(portable_folder)

        obsolete_folders = ['stdlib/test/', 'stdlib/lib2to3/tests/',
                            'stdlib/unittest/', 'stdlib/msilib/',
                            'stdlib/idlelib/', 'stdlib/ensurepip/',
                            'stdlib/distutils/']
        for folder in obsolete_folders:
            shutil.rmtree(os.path.join(portable_folder, folder), True)

        wx_zip = os.path.join(CACHE_DIR, arch, 'wx.zip')
        ZipFile(wx_zip, 'r').extractall(portable_libs)
        portable_exe_zip = os.path.join(CACHE_DIR, arch,
                                        '%s_portable.zip' % PROJECT)
        ZipFile(portable_exe_zip, 'r').extractall(portable_folder)

        for item in PKGS:
            src = os.path.join(SRC_DIR, item)
            echo_msg('Copying tree %s' % src)
            shutil.copytree(src, os.path.join(portable_libs, item))

        build.compile_sources(portable_folder)
        clear_files(portable_folder, ['py', 'so', 'pyo'])

        for item in EXTENSIONS:
            filename = os.path.basename(item)
            src = os.path.join(CACHE_DIR, arch, 'pyd', filename)
            dst = os.path.join(portable_libs, item)
            shutil.copy(src, dst)

        # Portable package compressing
        portable_zip = os.path.join(distro_folder, portable_name + '.zip')
        ziph = ZipFile(portable_zip, 'w', ZIP_DEFLATED)

        echo_msg('Compressing into %s' % portable_zip)
        for root, dirs, files in os.walk(portable_folder):
            for item in files:
                path = os.path.join(root, item)
                local_path = path.split(portable_name)[1][1:]
                ziph.write(path, os.path.join(portable_name, local_path))
        ziph.close()

        # MSI build
        echo_msg('Creating MSI package')

        clear_files(portable_folder, ['exe'])

        nonportable = os.path.join(CACHE_DIR, arch, '%s_msi.zip' % PROJECT)

        echo_msg('Extracting non-portable executables from %s' % nonportable)
        ZipFile(nonportable, 'r').extractall(portable_folder)

        msi_name = portable_name.replace('-portable', '')
        msi_data = {}
        msi_data.update(MSI_DATA)
        msi_data['_SourceDir'] = portable_folder
        if arch == 'win64':
            msi_data['Win64'] = 'yes'
            msi_data['_CheckX64'] = True
        msi_data['_OutputDir'] = distro_folder
        msi_data['_OutputName'] = msi_name + '_headless.msi'
        wixpy.build(msi_data)

        # Clearing
        shutil.rmtree(portable_folder, True)

    # Build clearing #####

    shutil.rmtree(BUILD_DIR, True)

    for item in ['MANIFEST', 'src/script/sk1', 'setup.cfg']:
        item = os.path.join(PROJECT_DIR, item)
        if os.path.lexists(item):
            os.remove(item)


############################################################
# Main build procedure
############################################################

option = sys.argv[1] if len(sys.argv) > 1 \
                        and not sys.argv[1].startswith('--') else ''
{
    'pull': pull_images,
    'rmi': remove_images,
    'rebuild_images': rebuild_images,
    'build': run_build,
    'build_local': run_build_local,
    'build_package': build_package,
    'msw_build': build_msw_packages,
    'packaging': packaging,
}.get(option, build_package)()
