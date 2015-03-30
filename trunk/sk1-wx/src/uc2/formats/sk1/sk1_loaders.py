# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

from uc2.formats.generic_filters import AbstractLoader
from uc2.formats.sk1 import sk1const

from uc2.formats.sk1.model import SK1Group
from uc2.formats.sk1.model import PolyBezier, Rectangle, Ellipse
from uc2.formats.sk1.model import Style
from uc2.formats.sk1.model import Trafo

class GenericLoader(AbstractLoader):

	name = 'Generic Loader'
	parent_stack = []

	def load(self, presenter, path):
		self.model = presenter.model
		self.active_page = self.model.pages.childs[0]
		self.active_layer = self.active_page.childs[-1]
		self.parent_stack = []
		self.parent_stack.append(self.active_layer)
		self.set_style()
		return AbstractLoader.load(self, presenter, path)

	def set_style(self, style=None):
		if style is None: self.style = Style()
		self.style = style

	def get_style(self):
		if self.style is None: self.style = Style()
		style = self.style
		self.style = Style()
		return style

	def __push(self):pass
	def __pop(self):pass

	def begin_composite(self, composite_class, args=(), kw=None):pass
	def end_composite(self):pass
	def end_all(self):pass
	def check_object(self, object):pass

	def append_object(self, obj):
		parent = self.parent_stack[-1]
		obj.parent = parent
		obj.config = self.config
		parent.childs.append(obj)

	def pop_last(self):pass

	def get_prop_stack(self):pass
	def set_prop_stack(self, stack):pass

	def document(self, *args, **kw):pass
	def layer(self, *args, **kw):pass
	def masterlayer(self, *args, **kw):pass
	def begin_page(self, *args, **kw):pass
	def end_layer(self):pass
	def begin_layer_class(self, layer_class, args, kw=None):pass

	def bezier(self, paths=None):
		obj = PolyBezier(paths=paths, properties=self.get_style())
		self.append_object(obj)

	def rectangle(self, m11, m21, m12, m22, v1, v2, radius1=0, radius2=0):
		trafo = Trafo(m11, m21, m12, m22, v1, v2)
		properties = self.get_style()
		obj = Rectangle(trafo, radius1, radius2, properties)
		self.append_object(obj)

	def ellipse(self, m11, m21, m12, m22, v1, v2, start_angle=0.0,
				end_angle=0.0, arc_type=sk1const.ArcPieSlice):
		trafo = Trafo(m11, m21, m12, m22, v1, v2)
		properties = self.get_prop_stack()
		obj = Ellipse(trafo, start_angle, end_angle, arc_type, properties)
		self.append_object(obj)

	def simple_text(self, str, trafo=None, valign=sk1const.ALIGN_BASE,
					halign=sk1const.ALIGN_LEFT):pass
	def image(self, image, trafo):pass

	def begin_group(self, *args, **kw):
		group = SK1Group()
		self.append_object(group)
		self.parent_stack.append(group)

	def end_group(self):
		self.parent_stack = self.parent_stack[:-1]

	def guess_cont(self):pass
	def add_meta(self, doc):pass
	def add_message(self, message):pass
	def Messages(self):pass


