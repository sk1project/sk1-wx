# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2019 by Maxim S. Barabash
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


DST_HEADER_SIZE = 512


DATA_TERMINATOR = b"\x1A"

DST_DOCUMENT = "DST Document"
DST_HEADER = "DST Header Document"
DST_UNKNOWN = "Unknown"

MASK_CMD = 0b11000011
CMD_STITCH = 0b00000011
CMD_SEQUIN_MODE = 0b01000011
CMD_JUMP = 0b10000011
CMD_CHANGE_COLOR = 0b11000011
CMD_STOP = 0b11110011

KNOWN_CMD = [
    CMD_STITCH, CMD_SEQUIN_MODE, CMD_JUMP, CMD_CHANGE_COLOR
]

CID_TO_NAME = {
    DST_UNKNOWN: "Unknown",
    CMD_STITCH: "Stitch",
    CMD_SEQUIN_MODE: "Sequin Mode",
    CMD_JUMP: "Jump",
    CMD_CHANGE_COLOR: "Change Color",
    CMD_STOP: "Stop",
    DATA_TERMINATOR: "Data terminator (Wilcom)",
}
