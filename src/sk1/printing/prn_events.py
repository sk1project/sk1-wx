# -*- coding: utf-8 -*-
#
#	Copyright (C) 2016 by Igor E. Novikov
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

"""
The package provides Qt-like signal-slot functionality
for printing events processing.

Signal arguments:
PRINTER_CHANGED	  prn - new printer instance 
PRINTER_MODIFIED  no args 
PRINTOUT_MODIFIED no args
"""

#Signal channels

PRINTER_CHANGED = ['PRINTER_CHANGED']
PRINTER_MODIFIED = ['PRINTER_MODIFIED']
PRINTOUT_MODIFIED = ['PRINTOUT_MODIFIED']

ALL_CHANNELS = [PRINTER_CHANGED, PRINTER_MODIFIED, PRINTOUT_MODIFIED]

def connect(channel, receiver):
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

def disconnect(channel, receiver):
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

def emit(channel, *args):
	"""
	Sends signal to all receivers in channel.
	"""
	try:
		for receiver in channel[1:]:
			try:
				if callable(receiver):
					receiver(*args)
			except:
				pass
	except:
		print "Cannot send signal to channel:", channel

def clean_channel(channel):
	"""
	Cleans channel queue.
	"""
	name = channel[0]
	channel[:] = []
	channel.append(name)

def clean_all_channels():
	"""
	Cleans all channels.
	"""
	for item in ALL_CHANNELS:
		clean_channel(item)

