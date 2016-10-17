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

import os, sys, shutil, commands

############################################################
#
# File system routines
#
############################################################

def get_dirs(path='.'):
	"""
	Return directory list for provided path
	"""
	list = []
	if path:
		if os.path.isdir(path):
			try:
				names = os.listdir(path)
			except os.error:
				return []
		names.sort()
		for name in names:
			if os.path.isdir(os.path.join(path, name)):
				list.append(name)
		return list

def get_dirs_withpath(path='.'):
	"""
	Return full  directory names list for provided path
	"""
	list = []
	names = []
	if os.path.isdir(path):
		try:
			names = os.listdir(path)
		except os.error:
			return names
	names.sort()
	for name in names:
		if os.path.isdir(os.path.join(path, name)) and not name == '.svn':
			list.append(os.path.join(path, name))
	return list

def get_files(path='.', ext='*'):
	"""
	Returns file list for provided path
	"""
	list = []
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
					list.append(name)
				elif '.' + ext == name[-1 * (len(ext) + 1):]:
					list.append(name)
	return list

def get_files_withpath(path='.', ext='*'):
	"""
	Returns full file names list for provided path
	"""
	import glob
	list = glob.glob(os.path.join(path, "*." + ext))
	list.sort()
	result = []
	for file in list:
		if os.path.isfile(file):
			result.append(file)
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
	for dir in dirs:
		list = get_files_withpath(dir, ext)
		list.sort()
		tree += list
	return tree

def generate_locales():
	"""
	Generates *.mo files Resources/Messages
	"""
	print 'LOCALES BUILD'
	files = get_files('po', 'po')
	if len(files):
		for file in files:
			lang = file.split('.')[0]
			po_file = os.path.join('po', file)
			mo_file = os.path.join('src', 'Resources', 'Messages', lang, 'LC_MESSAGES', 'skencil.mo')
			if not os.path.lexists(os.path.join('src', 'Resources', 'Messages', lang, 'LC_MESSAGES')):
				os.makedirs(os.path.join('src', 'share', 'Messages', lang, 'LC_MESSAGES'))
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

def make_source_list(path, file_list=[]):
	"""
	Returns list of paths for provided file list.
	"""
	ret = []
	for item in file_list:
		ret.append(os.path.join(path, item))
	return ret

INIT_FILE = '__init__.py'

def is_package(dir):
	"""
	Checks is provided directory a python package.
	"""
	if os.path.isdir(dir):
		marker = os.path.join(dir, INIT_FILE)
		if os.path.isfile(marker): return True
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
		except:pass
		for item in items:
			if item == '.svn':continue
			dir = os.path.join(path, item)
			if is_package(dir):
				packages.append(dir)
				packages += get_packages(dir)
	packages.sort()
	return packages

def get_package_dirs(path='src', excludes=[]):
	"""
	Collects root packages.
	"""
	dirs = {}
	items = []
	if os.path.isdir(path):
		try:
			items = os.listdir(path)
		except:pass
		for item in items:
			if item in excludes: continue
			if item == '.svn': continue
			dir = os.path.join(path, item)
			if is_package(dir):
				dirs[item] = dir
	return dirs


def get_source_structure(path='src', excludes=[]):
	"""
	Returns recursive list of python packages. 
	"""
	pkgs = []
	for item in get_packages(path):
		res = item.replace('\\', '.').replace('/', '.').split('src.')[1]
		check = True
		for exclude in excludes:
			if len(res) >= len(exclude) and res[:len(exclude)] == exclude:
				check = False
				break
		if check: pkgs.append(res)
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
	import string, platform, shutil

	version = (string.split(sys.version)[0])[0:3]
	machine = platform.machine()
	if os.name == 'posix':
		prefix = 'build/lib.linux-' + machine + '-' + version
		ext = '.so'
	elif os.name == 'nt' and platform.architecture()[0] == '32bit':
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
#--- PKG_CONFIG functions
#
############################################################

def get_pkg_includes(pkg_names):
	includes = []
	for item in pkg_names:
		output = commands.getoutput("pkg-config --cflags-only-I %s" % item)
		names = output.replace('-I', '').strip().split(' ')
		for name in names:
			if not name in includes: includes.append(name)
	return includes

def get_pkg_libs(pkg_names):
	libs = []
	for item in pkg_names:
		output = commands.getoutput("pkg-config --libs-only-l %s" % item)
		names = output.replace('-l', '').strip().split(' ')
		for name in names:
			if not name in libs: libs.append(name)
	return libs

def get_pkg_cflags(pkg_names):
	flags = []
	for item in pkg_names:
		output = commands.getoutput("pkg-config --cflags-only-other %s" % item)
		names = output.strip().split(' ')
		for name in names:
			if not name in flags: flags.append(name)
	return flags

############################################################
#
#--- DEB package builder
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

class DEB_Builder:
	"""
	Represents deb package build object.
	The object implements "setup.py bdist_deb" command.
	Works after regular "setup.py build" command and 
	constructs deb package using build result in build/ directory.
	Arguments:
	
	name - package names
	version - package version
	arch - system achitecture (amd64, i386, all), if not provided will be
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

	def __init__(self, name='',
				version='',
				arch='',
				maintainer='',
				depends='',
				section='',
				priority='',
				homepage='',
				description='',
				long_description='',
				package_dirs=[],
				package_data={},
				scripts=[],
				data_files=[],
				deb_scripts=[],
				dst=''):

		self.name = name
		self.version = version
		self.arch = arch
		self.maintainer = maintainer
		self.depends = depends
		if section:self.section = section
		if priority:self.priority = priority
		self.homepage = homepage
		self.description = description
		self.long_description = long_description

		self.package_dirs = package_dirs
		self.package_data = package_data
		self.scripts = scripts
		self.data_files = data_files
		self.deb_scripts = deb_scripts
		if dst: self.dst = dst

		self.package = 'python-%s' % self.name

		import string, platform
		self.py_version = (string.split(sys.version)[0])[0:3]

		if not self.arch:
			arch, bin = platform.architecture()
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

		self.package_name = 'python-%s-%s_%s.deb' % (self.name, self.version, self.arch)


	def info(self, msg, code=''):
		if code == ER_CODE: ret = '%s>>> %s' % (code, msg)
		elif not code: ret = msg
		else: ret = '%s: %s' % (code, msg)
		print ret

	def _make_dir(self, path):
		if not os.path.lexists(path):
			self.info('%s directory.' % path, MK_CODE)
			try: os.makedirs(path)
			except: raise IOError('Error while creating %s directory.') % path

	def clear_build(self):
		if os.path.lexists(self.build_dir):
			self.info('%s directory.' % self.build_dir, RM_CODE)
			if os.system('rm -rf ' + self.build_dir):
				raise IOError('Error while removing %s directory.' % self.build_dir)
		if os.path.lexists('dist'):
			self.info('Cleaning dist/ directory.', RM_CODE)
			if os.system('rm -rf dist/*.deb'):
				raise IOError('Error while cleaning dist/ directory.')
		else:
			self._make_dir('dist')

	def write_control(self):
		self._make_dir(self.deb_dir)
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
		self.info('Writing Debian control file.', MK_CODE)
		try:
			control = open(path, 'w')
			for item in control_list:
				name, val = item
				if val:
					if name: control.write('%s: %s\n' % (name, val))
					else: control.write('%s\n' % val)
			control.close()
		except:
			raise IOError('Error while writing Debian control file.')

	def copy_build(self):
		for item in os.listdir(self.src):
			path = os.path.join(self.src, item)
			if os.path.isdir(path):
				self.info('%s -> %s' % (path, self.dst), CP_CODE)
				if os.system('cp -R %s %s' % (path, self.dst)):
					raise IOError('Error while copying %s -> %s' % (path, self.dst))
			elif os.path.isfile(path):
				self.info('%s -> %s' % (path, self.dst), CP_CODE)
				if os.system('cp %s %s' % (path, self.dst)):
					raise IOError('Error while copying %s -> %s' % (path, self.dst))


	def copy_scripts(self, dir, scripts):
		if not scripts: return
		self._make_dir(dir)
		for item in scripts:
			self.info('%s -> %s' % (item, dir), CP_CODE)
			if os.system('cp %s %s' % (item, dir)):
				raise IOError('Cannot copying %s -> %s' % (item, dir))
			filename = os.path.basename(item)
			path = os.path.join(dir, filename)
			if os.path.isfile(path):
				self.info('%s as executable' % path, MK_CODE)
				if os.system('chmod +x %s' % path):
					raise IOError('Cannot set executable flag for %s' % path)

	def copy_files(self, path, files):
		if files and not os.path.isdir(path): self._make_dir(path)
		if not files:return
		for item in files:
			msg = '%s -> %s' % (item, path)
			if len(msg) > 80:msg = '%s -> \n%s%s' % (item, ' ' * 10, path)
			self.info(msg, CP_CODE)
			if os.system('cp %s %s' % (item, path)):
				raise IOError('Cannot copying %s -> %s' % (item, path))

	def copy_data_files(self):
		for item in self.data_files:
			path, files = item
			self.copy_files(self.build_dir + path, files)

	def copy_package_data_files(self):
		files = []
		pkgs = self.package_data.keys()
		for pkg in pkgs:
			items = self.package_data[pkg]
			for item in items:
				path = os.path.join(self.package_dirs[pkg], item)
				if os.path.basename(path) == '*.*':
					flist = []
					dir = os.path.join(self.dst, os.path.dirname(item))
					fldir = os.path.dirname(path)
					fls = os.listdir(fldir)
					for fl in fls:
						flpath = os.path.join(fldir, fl)
						if os.path.isfile(flpath):
							flist.append(flpath)
					files.append([dir, flist])
				else:
					if os.path.isfile(path):
						dir = os.path.join(self.dst, os.path.dirname(item))
						files.append([dir, [path, ]])
		for item in files:
			path, files = item
			self.copy_files(path, files)

	def make_package(self):
		self.info('%s package.' % self.package_name, MK_CODE)
		if os.system('dpkg --build %s/ dist/%s' % (self.build_dir, self.package_name)):
			raise IOError('Cannot create package %s' % self.package_name)

	def build(self):
		line = '=' * 30
		self.info(line + '\n' + 'DEB PACKAGE BUILD' + '\n' + line)
		try:
			if not os.path.isdir('build'):
				raise IOError('There is no project build! '
							'Run "setup.py build" and try again.')
			self.clear_build()
			self._make_dir(self.dst)
			self.copy_build()
			self.copy_scripts(self.bin_dir, self.scripts)
			self.copy_scripts(self.deb_dir, self.deb_scripts)
			self.copy_data_files()
			self.installed_size = str(int(get_size(self.build_dir) / 1024))
			self.write_control()
			self.make_package()
		except IOError as e:
			self.info(e, ER_CODE)
			self.info(line + '\n' + 'BUILD FAILED!')
			return 1
		self.info(line + '\n' + 'BUILD SUCCESSFUL!')
		return 0

