# -*- coding: utf-8 -*-
#
#	Copyright (C) 2012 by Igor E. Novikov
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

import gtk
import pango

from uc2 import uc2const
from uc2.formats.generic import GENERIC_TAGS, IDENT

from sword import _, events
from sword.tools.objectbrowser.toolbar import OIToolbar

class ObjectVisualizerWidget(gtk.VBox):

	active = False

	def __init__(self, app, presenter):

		gtk.VBox.__init__(self)
		self.app = app
		self.presenter = presenter

		entries = []
		if presenter.doc_presenter.model_type == uc2const.BINARY_MODEL:
			entries = [
				None,
				'EDIT_OBJ',
				'UPDATE_OBJ', ]

		self.toolbar = OIToolbar(self.app, entries)
		self.pack_start(self.toolbar, False, True)

		self.spacer = gtk.HBox()
		self.pack_end(self.spacer, False, True, 5)

		if presenter.doc_presenter.model_type == uc2const.TEXT_MODEL:
			self.viewer = TextDataViewer(self, app, presenter)
			self.pack_end(self.viewer, True, True)

		if presenter.doc_presenter.model_type == uc2const.TAGGED_MODEL:
			self.viewer = TaggedDataViewer(self, app, presenter)
			self.pack_end(self.viewer, True, True)

		try:
			if presenter.doc_presenter.model_type == uc2const.BINARY_MODEL:
				self.viewer = BinaryDataViewer(self, app, presenter)
				self.pack_end(self.viewer, True, True)
		except:
			import sys, traceback
			print sys.exc_info()[1].__str__() + '\n' + traceback.format_tb(sys.exc_info()[2])[0]

		self.show_all()

	def update_view(self):
		self.viewer.update_view()


class TextDataViewer(gtk.HBox):

	current_obj = None

	def __init__(self, parent, app, presenter):

		gtk.HBox.__init__(self)
		self.app = app
		self.presenter = presenter
		self.prnt = parent

		self.tb = gtk.TextBuffer()
		self.editor = gtk.TextView(self.tb)
		self.set_tags()
		self.editor.set_editable(False)
		self.editor.set_indent(5)
		self.editor.set_wrap_mode(gtk.WRAP_WORD_CHAR)

		self.sw = gtk.ScrolledWindow()
		self.sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.sw.add(self.editor)

		self.pack_start(self.sw, True, True, 5)
		self.show_all()

		eventloop = self.presenter.eventloop
		eventloop.connect(eventloop.SELECTION_CHANGED, self.reflect_selection)


	def reflect_selection(self, *args):
		self.current_obj = args[0][0][0]
		self.update_view()

	def update_view(self):
		obj = self.current_obj
		self.tb.set_text('')
		self.iter = self.tb.get_iter_at_offset(0)

		if obj.string:
			text = ''
			if obj.properties:
				for item in obj.properties:
					text += item + '\n'
			text += obj.string + '\n'
			if obj.end_string:
				text += obj.end_string + '\n'
			self.show_data(text)
		else:
			self.show_comment('No data')

	def show_data(self, text):
		self.tb.insert_with_tags_by_name(self.iter, text, "data")

	def show_comment(self, text):
		self.tb.insert_with_tags_by_name(self.iter, text, "comment")

	def set_tags(self):
		self.tb.create_tag("data",
                    weight=pango.WEIGHT_NORMAL,
                    size=15 * pango.SCALE)
		self.tb.create_tag("comment",
                    weight=pango.WEIGHT_NORMAL,
                    size=15 * pango.SCALE,
                    foreground="gray")


class TaggedDataViewer(gtk.HBox):

	current_obj = None

	def __init__(self, parent, app, presenter):

		gtk.HBox.__init__(self)
		self.app = app
		self.presenter = presenter
		self.prnt = parent

		self.tb = gtk.TextBuffer()
		self.editor = gtk.TextView(self.tb)
		self.set_tags()
		self.editor.set_editable(False)
		self.editor.set_indent(5)
		self.editor.set_wrap_mode(gtk.WRAP_NONE)

		self.sw = gtk.ScrolledWindow()
		self.sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.sw.add(self.editor)

		self.pack_start(self.sw, True, True, 5)
		self.show_all()

		eventloop = self.presenter.eventloop
		eventloop.connect(eventloop.SELECTION_CHANGED, self.reflect_selection)


	def reflect_selection(self, *args):
		self.current_obj = args[0][0][0]
		self.update_view()

	def update_view(self):
		obj = self.current_obj
		self.tb.set_text('')
		self.iter = self.tb.get_iter_at_offset(0)

		items = obj.__dict__.items()
		fields = []
		for key, value in items:
			if not key in GENERIC_TAGS:
				if not key[:6] == 'cache_':
					fields.append((key, value))

		if fields:
			self.show_tag('<' + obj.tag)
		else:
			if obj.childs:
				self.show_tag('<' + obj.tag)
			else:
				self.show_tag('<' + obj.tag + ' />\n')

		if fields:
			for key, value in fields:
				self.show_key('\n' + IDENT + str(key) + '=')
				value_str = str(value)
				if self.presenter.doc_presenter.cid == uc2const.PDXF:
					if isinstance(value, str):
						value_str = "'%s'" % (self.escape_quote(value_str))
				self.show_value('"' + value_str + '" ')

		if obj.childs:
			self.show_tag('>\n')
			self.show_comment(IDENT + _('...child content...') + '\n')
			self.show_tag('</' + obj.tag + '>\n')
		else:
			if fields:
				self.show_tag('/>\n')

	def escape_quote(self, line):
		return line.replace("'", "\\'")

	def show_tag(self, text):
		self.tb.insert_with_tags_by_name(self.iter, text, "tag")

	def show_key(self, text):
		self.tb.insert_with_tags_by_name(self.iter, text, "key")

	def show_value(self, text):
		self.tb.insert_with_tags_by_name(self.iter, text, "value")

	def show_comment(self, text):
		self.tb.insert_with_tags_by_name(self.iter, text, "comment")

	def set_tags(self):
		self.tb.create_tag("tag",
                    weight=pango.WEIGHT_BOLD,
                    size=14 * pango.SCALE)
		self.tb.create_tag("key",
                    weight=pango.WEIGHT_NORMAL,
                    size=14 * pango.SCALE,
                    foreground="#137936")
		self.tb.create_tag("value",
                    weight=pango.WEIGHT_NORMAL,
                    size=14 * pango.SCALE,
                    foreground="#AA0000")
		self.tb.create_tag("comment",
                    weight=pango.WEIGHT_NORMAL,
                    style=pango.STYLE_ITALIC,
                    size=14 * pango.SCALE,
                    foreground="gray")

def split_string(string, sub_length, char):
	result = []
	index = 0
	while index < len(string) / sub_length:
		result += [string[index * sub_length:(index + 1) * sub_length] + char]
		index += 1
	result += [string[index * sub_length:]]
	return result

def join_list_to_string(list):
	result = ''
	for item in list:
		result += item
	return result

COLORS = [
	('color01', '#80FF80'),
	('color02', '#FF8080'),
	('color04', '#B0B4FF'),
	('color03', '#D2D2D2'),
	('color05', '#FFFF80'),
	('color06', '#BAFFFA'),
	('color07', '#F7AEFF'),
	('color08', '#80FF80'),
	('color09', '#FF8080'),
	('color10', '#B0B4FF'),
	('color11', '#D2D2D2'),
	('color12', '#FFFF80'),
	('color13', '#BAFFFA'),
	('color14', '#F7AEFF'),
	]

LABEL_FG = '#BF5C00'
LABEL_FNT = "Courier New 10"

class BinaryDataViewer(gtk.HBox):

	current_obj = None

	def __init__(self, parent, app, presenter):

		gtk.HBox.__init__(self)
		self.app = app
		self.presenter = presenter
		self.prnt = parent

		self.tb = gtk.TextBuffer()
		self.editor = gtk.TextView(self.tb)
		self.editor.connect("button-release-event", self.check_selection)

		self.set_tags()
		self.editor.set_editable(False)
		self.editor.set_wrap_mode(gtk.WRAP_NONE)
		self.editor.set_border_width(1)
		self.editor.set_left_margin(3)
		self.editor.set_right_margin(3)
		self.editor.set_size_request(290, -1)

		self.num_label = gtk.Label()
		self.num_label.set_text('0000:0000')
		self.num_label.modify_font(pango.FontDescription(LABEL_FNT))
		self.num_label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(LABEL_FG))

		self.ascii_label = gtk.Label()
		self.ascii_label.modify_font(pango.FontDescription(LABEL_FNT))
		self.ascii_label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(LABEL_FG))

		vpack = gtk.VBox()
		hpack = gtk.HBox()
		num_vpack = gtk.VBox()
		num_vpack.pack_start(self.num_label, False)
		ascii_vpack = gtk.VBox()
		ascii_vpack.pack_start(self.ascii_label, False)

		hpack.pack_start(num_vpack, False, False, 2)
		hpack.pack_start(self.editor, False, False)
		hpack.pack_start(ascii_vpack, False, False, 2)

		num_line = gtk.Label('          0.1.2.3. 4.5.6.7. 8.9.a.b. c.d.e.f.')
		num_line.modify_font(pango.FontDescription(LABEL_FNT))
		num_line.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(LABEL_FG))
		num_line.set_alignment(0, 0.5)

		vpack.pack_start(num_line, False, True)
		vpack.pack_start(hpack)
		viewport = gtk.Viewport()
		viewport.add(vpack)


		self.sw = gtk.ScrolledWindow()
		self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.sw.add(viewport)

		self.pack_start(self.sw, True, True, 5)
		self.show_all()

		for item in COLORS:
			self.tb.create_tag(item[0], background=item[1])

		eventloop = self.presenter.eventloop
		eventloop.connect(eventloop.SELECTION_CHANGED, self.reflect_selection)

	def check_selection(self, *args):
		if self.tb.get_has_selection():
			range = self.tb.get_selection_bounds()
			if range:
				events.emit(events.BIN_SELECTION, self.tb.get_text(*range))
				return
		events.emit(events.BIN_SELECTION, '')


	def reflect_selection(self, *args):
		self.current_obj = args[0][0][0]
		if self.prnt.active:
			self.update_view()

	def update_view(self):
		obj = self.current_obj
		self.tb.set_text('')
		self.iter = self.tb.get_iter_at_offset(0)

		chunk = obj.chunk.encode('hex')
		lines = split_string(chunk, 16 * 2, '')
		formatted_chunk = ''
		orig_chunk = ''
		index = 0
		num_str = ''
		for line in lines:
			ln = join_list_to_string(split_string(line, 4 * 2, ' '))
			if len(ln) > 35:
				ln = ln[:35]

			formatted_chunk += ln + "\n"

			ascii_ln = line.decode('hex')
			ascii_ln_ = ''
			for char in ascii_ln:
				if ord(char) in range(0, 32) or ord(char) in range(127, 256):
					ascii_ln_ += '.'
				else:
					ascii_ln_ += char

			orig_chunk += ascii_ln_ + "\n"
			val = '%08x' % (index)
			num_str += val[:4] + ':' + val[4:] + '\n'
			index += 16

		while formatted_chunk[-1] in ['\n', ' ']:
			formatted_chunk = formatted_chunk[:-1]

		self.set_hex_data(formatted_chunk)
		self.num_label.set_text(num_str)
		self.ascii_label.set_text(orig_chunk)

		self.set_hex_data('\n\n')

		index = 0
		for item in self.current_obj.cache_fields:
			start = item[0]
			end = item[0] + item[1]
			start_shift = start / 4
			end_shift = end / 4
			start = start * 2 + start_shift
			end = end * 2 + end_shift
			if len(formatted_chunk) < end:
				end -= 1
			elif formatted_chunk[end - 1] == ' ':
				end -= 1
			self.tb.apply_tag_by_name(COLORS[index][0],
								self.tb.get_iter_at_offset(start),
								self.tb.get_iter_at_offset(end))

			offset = self.tb.get_end_iter().get_offset()
			self.set_hex_data('xxxx - ' + item[2] + '\n')
			self.tb.apply_tag_by_name(COLORS[index][0],
								self.tb.get_iter_at_offset(offset),
								self.tb.get_iter_at_offset(offset + 4))

			index += 1




	def set_hex_data(self, text):
		self.tb.insert_with_tags_by_name(self.iter, text, "hex")

	def set_tags(self):
		self.tb.create_tag("hex",
                    weight=pango.WEIGHT_NORMAL,
                    font='Courier New',
                    size=10 * pango.SCALE)
