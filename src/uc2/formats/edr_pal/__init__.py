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

# (EDR) Embird color palette
# NOTE: The .edr format is an optional color file

import os

REPLACEMENT_COLOR = "#000000"

DEFAULT_COLORS = {
    0: "#000000", 1: "#0E1F7C", 2: "#0A55A3",
    3: "#308777", 4: "#4B6BAF", 5: "#ED171F",
    6: "#D15C00", 7: "#913697", 8: "#E49ACB",
    9: "#915FAC", 10: "#9DD67D", 11: "#E8A900",
    12: "#FEBA35", 13: "#FFFF00", 14: "#70BC1F",
    15: "#C09400", 16: "#A8A8A8", 17: "#7B6F00",
    18: "#FFFFB3", 19: "#4F5556", 20: "#000000",
    21: "#0B3D91", 22: "#770176", 23: "#293133",
    24: "#2A1301", 25: "#F64A8A", 26: "#B27624",
    27: "#FCBBC4", 28: "#FE370F", 29: "#F0F0F0",
    30: "#6A1C8A", 31: "#A8DDC4", 32: "#2584BB",
    33: "#FEB343", 34: "#FFF08D", 35: "#D0A660",
    36: "#D15400", 37: "#66BA49", 38: "#134A46",
    39: "#878787", 40: "#D8CAC6", 41: "#435607",
    42: "#FEE3C5", 43: "#F993BC", 44: "#003822",
    45: "#B2AFD4", 46: "#686AB0", 47: "#EFE3B9",
    48: "#F73866", 49: "#B54C64", 50: "#132B1A",
    51: "#C70155", 52: "#FE9E32", 53: "#A8DEEB",
    54: "#00671A", 55: "#4E2990", 56: "#2F7E20",
    57: "#FDD9DE", 58: "#FFD911", 59: "#905BA6",
    60: "#F0F970", 61: "#E3F35B", 62: "#FFC864",
    63: "#FFC896", 64: "#FFC8C8", 65: "#000000",
}


class EDR_Palette(object):
    extension = ('.edr', '.EDR')
    colors = None
    index = 0

    def __init__(self, embroidery_filename=None):
        self.colors = {}
        self.load_palette(embroidery_filename)

    def load_palette(self, embroidery_filename=None, count=255):
        palette_filename = self.find_palette(embroidery_filename)
        if palette_filename:
            self.load_from_file(palette_filename, count)
        else:
            self.colors.update(DEFAULT_COLORS)

    def find_palette(self, embroidery_filename):
        if embroidery_filename:
            name = os.path.splitext(embroidery_filename)[0]
            for ext in self.extension:
                if os.path.exists(name + ext):
                    return name + ext

    def load_from_file(self, filename, count=255):
        with open(filename, 'rb') as stream:
            index = 0
            while index <= count:
                data = stream.read(4)
                if len(data) == 4:
                    hex_str = data[:3]
                    self.colors[index] = b'#%s' % hex_str.encode("hex")
                    index += 1
                else:
                    break

    def save_palette(self, filename):
        with open(filename, 'wb') as stream:
            for index in sorted(self.colors.keys()):
                hex_color = self.colors[index]
                record = b"%s\x00" % hex_color[1:].decode("hex")
                stream.write(record)

    def next_color(self, index=None):
        self.index = self.index + 1 if index is None else index
        return self.colors.get(self.index, REPLACEMENT_COLOR)
