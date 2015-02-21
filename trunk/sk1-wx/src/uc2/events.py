# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011 by Igor E. Novikov
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
for internal events processing.
"""

#Signal flags

CANCEL_OPERATION = False

#Signal channels

CONFIG_MODIFIED = ['CONFIG_MODIFIED']
FILTER_INFO = ['FILTER_INFO']
MESSAGES = ['MESSAGES']

def connect(channel, receiver):
	"""
	Connects signal receive method
	to provided channel. 
	"""
	if callable(receiver):
		try:
			channel.append(receiver)
		except:
			print "Cannot connect to channel:", channel, "receiver:", receiver

def disconnect(channel, receiver):
	"""
	Disconnects signal receive method
	from provided channel. 
	"""
	if callable(receiver):
		try:
			channel.remove(receiver)
		except:
			print "Cannot disconnect from channel:", channel, "receiver:", receiver

def emit(channel, *args):
	"""
	Sends signal to all receivers in channel.
	"""
#	print 'signal', channel[0]
	try:
		for receiver in channel[1:]:
			try:
				if callable(receiver):
					receiver(args)
			except:
				pass
	except:
		print "Cannot send signal to channel:", channel






