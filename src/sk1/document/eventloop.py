# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013 by Igor E. Novikov
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
            except Exception as e:
                msg = "Cannot connect to channel <%s> receiver: <%s> %s"
                LOG.error(msg, channel, receiver, e)

    def disconnect(self, channel, receiver):
        """
        Disconnects signal receive method
        from provided channel.
        """
        if callable(receiver):
            try:
                channel.remove(receiver)
            except Exception as e:
                msg = "Cannot disconnect from channel <%s> receiver: <%s> %s"
                LOG.error(msg, channel, receiver, e)

    def emit(self, channel, *args):
        """
        Sends signal to all receivers in channel.
        """
        for receiver in channel:
            try:
                if callable(receiver):
                    receiver(*args)
            except Exception as e:
                msg = 'Error calling <%s> receiver with %s %s'
                LOG.error(msg, receiver, args, e)
                continue
