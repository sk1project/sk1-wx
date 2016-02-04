# -*- coding: utf-8 -*-
#
#   Native modules build
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
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

import buildutils

from distutils.core import Extension


def make_modules(src_path, include_path):

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
			libraries=['cairo'])
	modules.append(cairo_module)

	pycms_src = os.path.join(src_path, 'uc2', 'cms')
	files = buildutils.make_source_list(pycms_src, ['_cms2.c', ])
	pycms_module = Extension('uc2.cms._cms',
			define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
			sources=files,
			libraries=['lcms2'],
			extra_compile_args=["-Wall"])
	modules.append(pycms_module)

	pango_src = os.path.join(src_path, 'uc2', 'libpango')
	files = buildutils.make_source_list(pango_src, ['_libpango.c', ])
	include_dirs = buildutils.make_source_list(include_path, ['cairo',
										'pycairo', 'pango-1.0', 'glib-2.0'])
	include_dirs += ['/usr/lib/x86_64-linux-gnu/glib-2.0/include/', ]
	pango_module = Extension('uc2.libpango._libpango',
			define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
			sources=files, include_dirs=include_dirs,
			library_dirs=['/usr/lib/x86_64-linux-gnu/'],
			libraries=['pango-1.0', 'pangocairo-1.0', 'cairo'])
	modules.append(pango_module)

	return modules
