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

from uc2 import _
from uc2.formats.generic import TextModelObject
from uc2.formats import pdxf

# Document object enumeration
HEADER = 1
START = 2
JOBS = 3
JOB = 4
COMMAND = 5
END = 6


CID_TO_NAME = {
	HEADER: _('HEADER'),
	START: _('START'),
	JOBS: _('JOBS'),
	JOB: _('JOB'),
	COMMAND: _('COMMAND'),
	END: _('END'),
	}

class PltModelObject(TextModelObject):
	"""
	Generic PLT model object.
	Provides common functionality for all model objects.
	"""

	def get_content(self):
		result = '' + self.string
		for child in self.childs:
			result += child.get_content()
		return result

	def resolve(self):
		is_leaf = True
		if self.childs: is_leaf = False
		name = CID_TO_NAME[self.cid]
		info = ''
		return (is_leaf, name, info)

class PltHeader(PltModelObject):
	"""
	Represents PLT model root instance. Can contains some PLT commands, but 
	usually is empthy. The main object role is to be parent instance for other
	PLT model objects. 
	
	The PLT file format is simplified version of HPGL file format and used for
	cutting plotters like Roland vinyl cutters. 
	(http://www.rolanddga.com/products/cutters/)
	
	Actually PLT file format has no tree-like data structure inside. Internal
	data are a sequence of HPGL commands like this:
	
	PU;PA0,0;SP;EC;PG1;EC1;OE;
	
	We have divided artificially the data on following chunks:
	[Header][Start command][Cutting path]... [Cutting path][End command]
	By this way we can build tree-like DOM model and easy process cutting data.
	"""

	cid = HEADER

	def __init__(self, string=''):
		self.string = string

class PltStart(PltModelObject):
	"""
	Represents a single PLT command "IN;"
	Expected that the command is unique in the file and means cutter job start.
	Object "string" field is set when object is instantiated.
	"""

	cid = START

	def __init__(self):
		self.string = 'IN;'

class PltEnd(PltModelObject):
	"""
	Represents a PLT command "PU;"
	Expected in the end of file to correctly finish plotter job.
	Object "string" field is set when object is instantiated.
	"""

	cid = END

	def __init__(self):
		self.string = 'PU;'

class PltCommand(PltModelObject):

	cid = COMMAND

	def __init__(self, string=''):
		self.string = string

class PltJobs(PltModelObject):
	"""
	Artificial object. Serves as a container for plotter cutting jobs.
	All cutting paths are stored in childs list.
	"""

	cid = JOBS

	def __init__(self, jobs=[]):
		if not jobs:
			self.childs = []


class PltJob(PltModelObject):

	"""
	Represents basic set of plotter commands. Corresponds a single unbreakable
	cutting path. Here is a sample of command set:
	
	PU454,11258;PD4787,11258;PD4787,8711;PD454,8711;PD454,11258;
	
	The command set is stored in "string" field. First PU command moves pen in 
	initial path point. Other commands are PD commands and put down pen and do 
	cutting job.
	
	Field "cache_path" store a path representation as PDXF path. Used for model 
	translation into or from PDXF file format. Here is a sample of cache_path
	content:
	
	[[454,11258],[[4787,11258],[4787,8711],[454,8711],[454,11258]],0]
	
	cache_path point coordinates are in PLT coordinate system i.e. there is no
	negative values and all numbers are in 40 points per millimeter dimension.
	"""

	cid = JOB
	cache_path = []

	def __init__(self, string='', path=[]):
		self.string = string
		self.cache_path = path

	def update(self):
		if self.string and not self.cache_path:
			path = []
			cmd = ''
			cmd += self.string
			cmd = cmd.replace(";", "],")
			cmd = cmd.replace("PU", "[")
			cmd = cmd.replace("PD", "[")
			cmd = 'path=[%s]' % (cmd)
			code = compile(cmd, '<string>', 'exec')
			exec code
			self.cache_path = []
			self.cache_path.append(path[0])
			self.cache_path.append(path[1:])
			self.cache_path.append(pdxf.const.CURVE_OPENED)


		elif self.cache_path and not self.string:
			self.string = 'PU%d,%d;' % (self.cache_path[0][0], self.cache_path[0][1])
			for point in self.cache_path[1]:
				self.string += 'PD%d,%d;' % (point[0], point[1])



