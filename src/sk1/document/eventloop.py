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

class EventLoop:

	presenter = None

	VIEW_CHANGED = []
	SELECT_AREA = []
	DOC_MODIFIED = []
	SELECTION_CHANGED = []
	PAGE_CHANGED = []

	def __init__(self, presenter):
		self.presenter = presenter
		self.VIEW_CHANGED = []
		self.SELECT_AREA = []
		self.DOC_MODIFIED = []
		self.SELECTION_CHANGED = []
		self.PAGE_CHANGED = []

	def destroy(self):
		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	def connect(self, channel, receiver):
		"""
		Connects signal receive method
		to provided channel. 
		"""
		if callable(receiver):
			try:
				channel.append(receiver)
			except:
				msg = "Cannot connect to channel:"
				print msg, channel, "receiver:", receiver

	def disconnect(self, channel, receiver):
		"""
		Disconnects signal receive method
		from provided channel. 
		"""
		if callable(receiver):
			try:
				channel.remove(receiver)
			except:
				msg = "Cannot disconnect from channel:"
				print msg, channel, "receiver:", receiver

	def emit(self, channel, *args):
		"""
		Sends signal to all receivers in channel.
		"""
#		print 'signal', channel, args
		try:
			for receiver in channel:
				try:
					if callable(receiver):
						receiver(args)
				except:
#					print 'error', receiver
					pass
		except:
			print "Cannot send signal to channel:", channel
