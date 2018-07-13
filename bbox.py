#!/usr/bin/env python2
#
#   BuildBox for sK1/UniConvertor 2.x
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
BuildBox can be used with Vagrant VM. To run in VM:

>vagrant up ubuntu
>vagrant ssh ubuntu
>sudo -s
>/vagrant/bbox.py build
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
UC2 = 'uc2'
PROJECT = SK1  # change point

# Build constants
IMAGE_PREFIX = 'sk1project/'
VAGRANT_DIR = '/vagrant'
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(PROJECT_DIR, 'build')
DIST_DIR = os.path.join(PROJECT_DIR, 'dist')
RELEASE_DIR = os.path.join(PROJECT_DIR, 'release')
PKGBUILD_DIR = os.path.join(PROJECT_DIR, 'pkgbuild')
ARCH_DIR = os.path.join(PROJECT_DIR, 'archlinux')

SCRIPT = 'setup-%s.py' % PROJECT
APP_NAME = PROJECT
APP_VER = '2.0rc4'

RELEASE = False
DEBUG_MODE = True

IMAGES = [
    'ubuntu_14.04_32bit',
    'ubuntu_14.04_64bit',
    'ubuntu_16.04_32bit',
    'ubuntu_16.04_64bit',
    'ubuntu_17.10_64bit',
    'ubuntu_18.04_64bit',
    'debian_7_32bit',
    'debian_7_64bit',
    'debian_8_32bit',
    'debian_8_64bit',
    'debian_9_32bit',
    'debian_9_64bit',
    'fedora_26_64bit',
    'fedora_27_64bit',
    'fedora_28_64bit',
    'opensuse_42.3_64bit',
    'opensuse_15.0_64bit',
    'msw-packager'
]


def clear_folders():
    # Clear build folders
    if is_path(BUILD_DIR):
        command('rm -rf %s' % BUILD_DIR)
    if is_path(DIST_DIR):
        command('rm -rf %s' % DIST_DIR)
    if not is_path(RELEASE_DIR):
        os.makedirs(RELEASE_DIR)


def clear_files(folder, ext='py'):
    for path in get_files_tree(folder, ext):
        if os.path.exists(path) and path.endswith(ext):
            os.remove(path)


############################################################
# Main functions
############################################################


def pull_images():
    for image in IMAGES:
        echo_msg('Pulling %s%s image' % (IMAGE_PREFIX, image),
                 code=STDOUT_GREEN)
        command('docker pull %s%s' % (IMAGE_PREFIX, image))


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


def run_build():
    echo_msg('BuildBox started', code=STDOUT_MAGENTA)
    echo_msg('=' * 30, code=STDOUT_MAGENTA)
    if VAGRANT_DIR != PROJECT_DIR:
        if is_path(VAGRANT_DIR):
            command('rm -f %s' % VAGRANT_DIR)
        command('ln -s %s %s' % (PROJECT_DIR, VAGRANT_DIR))
    if is_path(RELEASE_DIR):
        command('rm -rf %s' % RELEASE_DIR)
    for image in IMAGES:
        os_name = image.capitalize().replace('_', ' ')
        echo_msg('Build on %s' % os_name, code=STDOUT_YELLOW)
        output = ' 1> /dev/null' if not DEBUG_MODE else ''
        if command('docker run --rm -v %s:%s %s%s %s' %
                   (PROJECT_DIR, VAGRANT_DIR, IMAGE_PREFIX, image, output)):
            echo_msg('=' * 30 + '> FAIL', code=STDOUT_FAIL)
        else:
            echo_msg('=' * 30 + '> OK', code=STDOUT_GREEN)
    command('chmod -R 777 %s' % RELEASE_DIR)
    if VAGRANT_DIR != PROJECT_DIR:
        command('rm -f %s' % VAGRANT_DIR)


def build_package():
    mint_folder = os.path.join(RELEASE_DIR, 'LinuxMint')
    eos_folder = os.path.join(RELEASE_DIR, 'elementaryOS')
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

MSI_DATA = {
    # Required
    'Name': 'sK1 2.0',
    'UpgradeCode': '3AC4B4FF-10C4-4B8F-81AD-BAC3238BF693',
    'Version': '2.0rc4',
    # Optional
    'Manufacturer': 'sK1 Project',
    'Description': 'sK1 2.0 Installer',
    'Comments': 'Licensed under GPL v3',
    'Keywords': 'Vector graphics, Prepress',
    # Language
    'Language': '1033',
    'Languages': '1033',
    'Codepage': '1252',
    # Internals
    'InstallerVersion': '200',
    'Compressed': 'yes',

    # Structural elements
    '_Icon': '/win32-devres/sk1.ico',
    '_ProgramMenuFolder': 'sK1 Project',
    '_Shotcuts': [
        {'Name': '',
         'Description': '',
         'Target': 'sk1.exe'},
    ],
    '_Arch': 'x86',
    '_SourceDir': '.',
    '_OutputName': '',

}


def build_msw_packages():
    echo_msg('Creating portable package')
    distro_folder = os.path.join(RELEASE_DIR, 'MS_Windows')
    out = ' 1> /dev/null  2> /dev/null' if not DEBUG_MODE else ''

    clear_folders()
    if os.path.isdir(DIST_DIR):
        shutil.rmtree(DIST_DIR, True)

    command('cd %s;python2 %s build %s' % (PROJECT_DIR, SCRIPT, out))
    libdir = os.path.join(BUILD_DIR, 'lib.linux-x86_64-2.7')
    build.compile_sources(libdir)
    clear_files(libdir)
    clear_files(libdir, 'so')

    for arch in ['win32', 'win64']:
        portable_name = '%s-%s-%s-portable' % (APP_NAME, APP_VER, arch)
        if not RELEASE:
            portable_name = '%s-%s-%s-%s-portable' % \
                            (APP_NAME, APP_VER, TIMESTAMP, arch)
        portable_folder = os.path.join(PROJECT_DIR, portable_name)
        if os.path.exists(portable_folder):
            shutil.rmtree(portable_folder, True)
        os.mkdir(portable_folder)
        portable = os.path.join('/%s-devres' % arch, 'portable.zip')

        echo_msg('Extracting portable files from %s' % portable)
        ZipFile(portable, 'r').extractall(portable_folder)

        build.compile_sources(portable_folder)
        clear_files(portable_folder)

        portable_libs = os.path.join(portable_folder, 'libs')
        for item in PKGS:
            src = os.path.join(libdir, item)
            echo_msg('Copying tree %s' % src)
            shutil.copytree(src, os.path.join(portable_libs, item))

        for item in EXTENSIONS:
            filename = os.path.basename(item)
            src = os.path.join('/%s-devres' % arch, 'pyd', filename)
            dst = os.path.join(portable_libs, item)
            shutil.copy(src, dst)

        if not is_path(distro_folder):
            os.makedirs(distro_folder)

        portable_zip = os.path.join(distro_folder, portable_name + '.zip')
        ziph = ZipFile(portable_zip, 'w', ZIP_DEFLATED)

        echo_msg('Compressing into %s' % portable_zip)
        for root, dirs, files in os.walk(portable_folder):
            for item in files:
                path = os.path.join(root, item)
                local_path = path.split(portable_name)[1][1:]
                ziph.write(path, os.path.join(portable_name, local_path))
        ziph.close()
        shutil.rmtree(portable_folder, True)

    # Build clearing #####

    shutil.rmtree(BUILD_DIR, True)

    for item in ['MANIFEST', 'MANIFEST.in', 'src/script/sk1',
                 'src/script/uniconvertor', 'setup.cfg']:
        item = os.path.join(PROJECT_DIR, item)
        if os.path.lexists(item):
            os.remove(item)


############################################################
# Main build procedure
############################################################

option = sys.argv[1] if len(sys.argv) > 1 else ''
{
    'pull': pull_images,
    'rmi': remove_images,
    'rebuild_images': rebuild_images,
    'build': run_build,
    'msw_build': build_msw_packages,
}.get(option, build_package)()
