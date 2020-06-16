# -*- coding: utf-8 -*-
#
#  Copyright (C) 2011-2017 by Ihor E. Novikov
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

LOG = logging.getLogger(__name__)

"""
Module provides Qt-like signal-slot functionality
for internal events processing.

Signal arguments:
CONFIG_MODIFIED   attr, value - modified config field
APP_STATUS		  msg - statusbar message
MOUSE_STATUS	  msg - mouse status msg
CMS_CHANGED		  no args 
HISTORY_CHANGED	  no args 
NO_DOCS		      no args
DOC_MODIFIED	  doc - presenter instance
DOC_CHANGED	      doc - actual presenter instance
DOC_SAVED		  doc - saved presenter instance
DOC_CLOSED		  no args
MODE_CHANGED	  mode - canvas MODE value
SELECTION_CHANGED doc - presenter instance
CLIPBOARD		  no args 
PAGE_CHANGED      doc - presenter instance
SNAP_CHANGED	  no args
UPDATE_CHANNEL    id - recipient id 
"""

# Signal channels

CONFIG_MODIFIED = ['CONFIG_MODIFIED']

APP_STATUS = ['APP_STATUS']
MOUSE_STATUS = ['MOUSE_STATUS']
CMS_CHANGED = ['CMS_CHANGED']
HISTORY_CHANGED = ['HISTORY_CHANGED']

NO_DOCS = ['NO_DOCS']
DOC_MODIFIED = ['DOC_MODIFIED']
DOC_CHANGED = ['DOC_CHANGED']
DOC_SAVED = ['DOC_SAVED']
DOC_CLOSED = ['DOC_CLOSED']

MODE_CHANGED = ['MODE_CHANGED']
SELECTION_CHANGED = ['SELECTION_CHANGED']
CLIPBOARD = ['CLIPBOARD']
PAGE_CHANGED = ['PAGE_CHANGED']
SNAP_CHANGED = ['SNAP_CHANGED']
UPDATE_CHANNEL = ['UPDATE_CHANNEL']

ALL_CHANNELS = [CONFIG_MODIFIED, APP_STATUS, MOUSE_STATUS, CMS_CHANGED,
                HISTORY_CHANGED, NO_DOCS, DOC_MODIFIED, DOC_CHANGED, DOC_SAVED,
                DOC_CLOSED, MODE_CHANGED, SELECTION_CHANGED, CLIPBOARD,
                PAGE_CHANGED, SNAP_CHANGED]

ET_ID = 'EDIT_TEXT_MODE'


def connect(channel, receiver):
    """
    Connects signal receive method
    to provided channel.
    """
    if callable(receiver):
        try:
            channel.append(receiver)
        except Exception:
            msg = "Cannot connect to channel <%s> receiver: <%s> %s"
            LOG.exception(msg, channel, receiver)


def disconnect(channel, receiver):
    """
    Disconnects signal receive method
    from provided channel.
    """
    if callable(receiver):
        try:
            channel.remove(receiver)
        except Exception:
            msg = "Cannot disconnect from channel <%s> receiver: <%s> %s"
            LOG.exception(msg, channel, receiver)


def emit(channel, *args):
    """
    Sends signal to all receivers in channel.
    """
    for receiver in channel[1:]:
        try:
            if callable(receiver):
                receiver(*args)
        except Exception:
            msg = 'Error calling <%s> receiver with %s %s'
            LOG.exception(msg, receiver, args)
            continue


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
