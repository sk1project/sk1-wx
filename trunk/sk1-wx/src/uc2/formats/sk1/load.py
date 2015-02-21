# -*- coding: utf-8 -*-

# Copyright (C) 2003-2006 by Igor E. Novikov
# Copyright (C) 1997, 1998, 1999, 2000, 2001, 2003 by Bernhard Herzog
#
# This library is covered by GNU Library General Public License.
# For more info see COPYRIGHTS file in sK1 root directory.



# This file contains various classes for reading a drawing from (ASCII)
# files.
#
# Classes:
#
# LoaderWithComposites
# GenericLoader(LoaderWithComposites)
#
#	Two classes that provide common functions for the format
#	specific classes.
#
# Functions
#
# load_drawing(filename)
#
#	Determines the type of the file (by reading a few lines) and
#	invokes the appropriate import filter. Return the newly created
#	document.
#

from types import StringType, TupleType
import os, string
from copy import deepcopy

from uc2 import _
from uc2.formats.sk1 import sk1const

from uc2.formats.sk1.model import SK1Document, SK1Pages, SK1Page, SK1Layer
from uc2.formats.sk1.model import SK1Group
from uc2.formats.sk1.model import PolyBezier, Rectangle, Ellipse, SK1Image
from uc2.formats.sk1.model import EmptyPattern, Style

from app import PropertyStack

from uc2.formats.sk1.model import Trafo, Translation

doc_class = SK1Document
pages_class = SK1Pages
page_class = SK1Page


# The loaders usually intercept exceptions raised while reading and
# raise a SketchLoadError instead. Setting the following variable to
# true will prohibit this. (useful only for debugging a loader)
#
# XXX this is better done by using warn_tb(INTERNAL,...) before
# reraising the exception as a SketchLoadError.
_dont_handle_exceptions = 0


class LoaderWithComposites:

	guess_continuity = 0
	page_layout = None

	def __init__(self):
		self.composite_stack = None
		self.composite_items = []
		self.composite_class = None
		self.composite_args = None
		self.object = None

	def __push(self):
		self.composite_stack = (self.composite_class,
								self.composite_args,
								self.composite_items,
								self.composite_stack)

	def __pop(self):
		(self.composite_class, self.composite_args,
			self.composite_items, self.composite_stack) = self.composite_stack

	def begin_composite(self, composite_class, args=(), kw=None):
		self.__push()
		self.composite_class = composite_class
		self.composite_args = (args, kw)
		self.composite_items = []
		self.object = None

	def end_composite(self):
		if self.composite_class:
			args, kw = self.composite_args
			if not kw:
				kw = {}
			composite = apply(self.composite_class, args, kw)
			# We treat Plugins specially here and in check_object so
			# that we can be a bit more lenient with plugin objects.
			# They should not be empty (after all they'd be invisible
			# then) but they might. If they're empty they're simply
			# ignored
			if self.composite_items or composite.can_be_empty \
					or composite.is_Plugin:
				append = composite.load_AppendObject
				for item in self.composite_items:
					if self.check_object(item):
						append(item)
				composite.load_Done()
				self.__pop()
				self.append_object(composite)
			else:
				self.__pop()
				#may be just pass the problem?
				#raise EmptyCompositeError
		else:
			print 'ERROR: no composite to end'
#			raise SketchLoadError('no composite to end')

	def end_all(self):
		while self.composite_stack:
			self.end_composite()

	def check_object(self, object):
		# Return true if object is OK. Currently this just checks the
		# following things:
		#
		# - whether a bezier object has at least one path and all paths
		#   have at least length 1.
		# - for bezier objects, guess the continuity if
		#   self.guess_continuity is true.
		# - Whether a plugin object is not empty
		result = 1
		if object.is_Bezier:
			paths = object.Paths()
			if len(paths) >= 1:
				for path in paths:
					if path.len == 0:
						result = 0
						break
			else:
				result = 0
			if result and self.guess_continuity:
				object.guess_continuity()
		elif object.is_Plugin:
			result = len(object.GetObjects())
		return result

	def append_object(self, object):
		self.composite_items.append(object)
		self.object = object

	def pop_last(self):
		# remove the last object in self.composite_items and return it
		object = None
		if self.composite_items:
			object = self.composite_items[-1]
			del self.composite_items[-1]
			if self.composite_items:
				self.object = self.composite_items[-1]
			else:
				self.object = None
		return object


class GenericLoader(LoaderWithComposites):

	format_name = ''

	base_style = None

	def __init__(self, file, filename, match):
		LoaderWithComposites.__init__(self)
		self.file = file
		self.filename = filename
		self.match = match
		self.style = Style()
		if self.base_style is not None:
			self.prop_stack = PropertyStack(base=self.base_style.Duplicate())
		else:
			self.prop_stack = PropertyStack()
		self.messages = {}

	def get_prop_stack(self):
		stack = self.prop_stack
		if not self.style.IsEmpty():
			stack.load_AddStyle(self.style)
		stack.condense()
		if self.base_style is not None:
			self.prop_stack = PropertyStack(base=self.base_style.Duplicate())
		else:
			self.prop_stack = PropertyStack()
		self.style = Style()
		return stack

	def set_prop_stack(self, stack):
		self.prop_stack = stack

	def document(self, *args, **kw):
		self.begin_composite(doc_class, args, kw)

	def layer(self, *args, **kw):
		self.begin_layer_class(SK1Layer, args, kw)

	def masterlayer(self, *args, **kw):
		while not issubclass(self.composite_class, doc_class):
			self.end_composite()
		kw['is_MasterLayer'] = 1
		self.begin_layer_class(SK1Layer, args, kw)

	def begin_page(self, *args, **kw):
		while not issubclass(self.composite_class, doc_class):
			self.end_composite()
		if not len(args):
			args = ["", deepcopy(self.page_layout)]
		self.begin_composite(page_class, args, kw)

	def end_layer(self):
		self.end_composite()

	def begin_layer_class(self, layer_class, args, kw=None):
		if issubclass(self.composite_class, SK1Layer):
			self.end_composite()
		if issubclass(self.composite_class, doc_class) or issubclass(self.composite_class, page_class):
			self.begin_composite(layer_class, args, kw)
		else:
			print 'self.composite_class is %s, not a document', self.composite_class
#			raise SketchLoadError('self.composite_class is %s, not a document',
#									self.composite_class)

	def bezier(self, paths=None):
		self.append_object(PolyBezier(paths=paths,
										properties=self.get_prop_stack()))

	def rectangle(self, m11, m21, m12, m22, v1, v2, radius1=0, radius2=0):
		trafo = Trafo(m11, m21, m12, m22, v1, v2)
		self.append_object(Rectangle(trafo, radius1=radius1,
										radius2=radius2,
										properties=self.get_prop_stack()))

	def ellipse(self, m11, m21, m12, m22, v1, v2, start_angle=0.0,
				end_angle=0.0, arc_type=sk1const.ArcPieSlice):
		self.append_object(Ellipse(Trafo(m11, m21, m12, m22, v1, v2),
									start_angle, end_angle, arc_type,
									properties=self.get_prop_stack()))
	def simple_text(self, str, trafo=None, valign=sk1const.ALIGN_BASE,
					halign=sk1const.ALIGN_LEFT):
		if type(trafo) == TupleType:
			if len(trafo) == 2:
				trafo = apply(Translation, trafo)
			else:
				raise TypeError, "trafo must be a Trafo-object or a 2-tuple"
		self.append_object(text.SimpleText(text=str, trafo=trafo,
											valign=valign, halign=halign,
											properties=self.get_prop_stack()))

	def image(self, image, trafo):
		if type(trafo) == TupleType:
			if len(trafo) == 2:
				trafo = apply(Translation, trafo)
			else:
				raise TypeError, "trafo must be a Trafo-object or a 2-tuple"
		self.append_object(SK1Image(image, trafo=trafo))

	def begin_group(self, *args, **kw):
		self.begin_composite(SK1Group, args, kw)

	def end_group(self):
		self.end_composite()

	def guess_cont(self):
		self.guess_continuity = 1

	def end_composite(self):
		isdoc = self.composite_class is doc_class
		LoaderWithComposites.end_composite(self)
		if isdoc:
			self.add_meta(self.object)

	def add_meta(self, doc):
		doc.meta.fullpathname = self.filename
		dir, name = os.path.split(self.filename)
		doc.meta.directory = dir
		doc.meta.filename = name
		doc.meta.native_format = 0
		doc.meta.format_name = self.format_name

	def add_message(self, message):
#		pdebug(('load', 'echo_messages'), message)
		self.messages[message] = self.messages.get(message, 0) + 1

	def Messages(self):
		messages = self.messages.items()
		list = []
		for message, count in messages:
			if count > 1:
				list.append(_("%(message)s (%(count)d times)") % locals())
			else:
				list.append(message)
		list.sort()
		return string.join(list, '\n')


class SimplifiedLoader(GenericLoader):

	def __init__(self, file, filename, match):
		GenericLoader.__init__(self, file, filename, match)
		self.lineno = 1 # first line has been read

	def readline(self):
		line = self.file.readline()
		self.lineno = self.lineno + 1
		return line

	def set_properties(self, **kw):
		style = self.style
		for key, value in kw.items():
			setattr(style, key, value)

	def empty_line(self):
		self.style.line_pattern = EmptyPattern

	def empty_fill(self):
		self.style.fill_pattern = EmptyPattern



#do_profile = 0
#def load_drawing_from_file(file, filename = '', doc_class = None):
#	# Note: the doc_class argument is only here for plugin interface
#	# compatibility with 0.7 (especiall e.g. gziploader)
#	line = file.readline()
#	# XXX ugly hack for riff-based files, e.g. Corel's CMX. The length
#	# might contain newline characters.
#	if line[:4] == 'RIFF' and len(line) < 12:
#		line = line + file.read(12 - len(line))
#	for info in filters.import_plugins:
#		match = info.rx_magic.match(line)
#		if match:
#			loader = info(file, filename, match)
#			try:
#				try:
#					if do_profile:
#						import profile
#						warn(INTERNAL, 'profiling...')
#						prof = profile.Profile()
#						prof.runctx('loader.Load()', globals(), locals())
#						prof.dump_stats(os.path.join(info.dir, info.module_name + '.prof'))
#						warn(INTERNAL, 'profiling... (done)')
#						doc = loader.object
#					else:
#						#t = time.clock()
#						doc = loader.Load()
#						#print 'load in', time.clock() - t, 'sec.'
#					messages = loader.Messages()
#					if messages:
#						doc.meta.load_messages = messages
#					return doc
#				except Exception, value:
#					raise SketchLoadError(_("Parsing error:")+" "+ str(value))
#								
#			finally:
#				info.UnloadPlugin()
#	else:
#		raise SketchLoadError(_("unrecognised file type"))
#
#
#def load_drawing(filename):
#	if type(filename) == StringType:
#		name=locale_utils.utf_to_locale(filename)
#		#name=locale_utils.strip_line(name)
#		try:
#			file = open(name, 'rb')
#		except IOError, value:
#			message = value.strerror
#			raise SketchLoadError(_("Cannot open %(filename)s:\n%(message)s")
#									% locals())
#	else:
#		# assume a file object. This does not happen at the moment and
#		# SKLoder requires the filename for external objects.
#		file = filename
#		filename = ''
#	return load_drawing_from_file(file, filename)
