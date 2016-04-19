# -*- coding: utf-8 -*-
#
#   Native modules build
#
# 	Copyright (C) 2015-2016 by Igor E. Novikov
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

import buildutils, commands

from distutils.core import Extension


def make_modules(src_path, include_path, lib_path=[]):

	modules = []

	filter_src = os.path.join(src_path, 'uc2', 'utils', 'streamfilter')
	files = ['streamfilter.c', 'filterobj.c', 'linefilter.c',
			'subfilefilter.c', 'base64filter.c', 'nullfilter.c',
			'stringfilter.c', 'binfile.c', 'hexfilter.c']
	files = buildutils.make_source_list(filter_src, files)
	filter_module = Extension('uc2.utils.streamfilter',
			define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
			sources=files)
	modules.append(filter_module)

	sk1objs_src = os.path.join(src_path, 'uc2', 'formats', 'sk1', 'sk1objs')
	files = ['_sketchmodule.c', 'skpoint.c', 'skcolor.c', 'sktrafo.c',
		'skrect.c', 'skfm.c', 'curvefunc.c', 'curveobject.c', 'curvelow.c',
		'curvemisc.c', 'skaux.c', 'skimage.c', ]
	files = buildutils.make_source_list(sk1objs_src, files)
	sk1objs_module = Extension('uc2.formats.sk1._sk1objs',
			define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
			sources=files)
	modules.append(sk1objs_module)

	cairo_src = os.path.join(src_path, 'uc2', 'libcairo')
	files = buildutils.make_source_list(cairo_src, ['_libcairo.c', ])
	include_dirs = buildutils.make_source_list(include_path, ['cairo', 'pycairo'])
	cairo_module = Extension('uc2.libcairo._libcairo',
			define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
			sources=files, include_dirs=include_dirs,
			library_dirs=lib_path,
			libraries=['cairo'])
	modules.append(cairo_module)

	if os.name == 'nt':
		pycms_files = ['_cms.c', ]
		pycms_libraries = ['lcms']
	else:
		pycms_files = ['_cms2.c', ]
		pycms_libraries = ['lcms2']

	pycms_src = os.path.join(src_path, 'uc2', 'cms')
	files = buildutils.make_source_list(pycms_src, pycms_files)
	include_dirs = [include_path, ]
	pycms_module = Extension('uc2.cms._cms',
			define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
			sources=files, include_dirs=include_dirs,
			library_dirs=lib_path,
			libraries=pycms_libraries,
			extra_compile_args=["-Wall"])
	modules.append(pycms_module)

	pango_src = os.path.join(src_path, 'uc2', 'libpango')
	files = buildutils.make_source_list(pango_src, ['_libpango.c', ])
	include_dirs = buildutils.make_source_list(include_path, ['cairo',
										'pycairo', 'pango-1.0', 'glib-2.0'])
	if os.name == 'posix':
		output = commands.getoutput("pkg-config --cflags glib-2.0")
		include_dirs += output.replace('-I', '').strip().split(' ')
	pango_module = Extension('uc2.libpango._libpango',
			define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
			sources=files, include_dirs=include_dirs,
			library_dirs=lib_path,
			libraries=['pango-1.0', 'pangocairo-1.0', 'cairo',
					'glib-2.0', 'gobject-2.0'])
	modules.append(pango_module)

	libimg_src = os.path.join(src_path, 'uc2', 'libimg')
	files = buildutils.make_source_list(libimg_src, ['_libimg.c', ])
	include_dirs = [include_path, include_path + '/ImageMagick']
	libimg_module = Extension('uc2.libimg._libimg',
			define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
			sources=files, include_dirs=include_dirs,
			library_dirs=lib_path,
			libraries=['MagickWand'])
	modules.append(libimg_module)

	return modules
