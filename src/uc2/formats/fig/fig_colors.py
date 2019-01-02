# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Maxim S. Barabash
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

from uc2.uc2const import COLOR_RGB
from uc2 import cms


FIG_COLORS = {
    -1: [COLOR_RGB, [0.00, 0.00, 0.00], 1.0, '.'],
    0:  [COLOR_RGB, [0.00, 0.00, 0.00], 1.0, 'black'],
    1:  [COLOR_RGB, [0.00, 0.00, 1.00], 1.0, 'blue'],
    2:  [COLOR_RGB, [0.00, 1.00, 0.00], 1.0, 'green'],
    3:  [COLOR_RGB, [0.00, 1.00, 1.00], 1.0, 'cyan'],
    4:  [COLOR_RGB, [1.00, 0.00, 0.00], 1.0, 'red'],
    5:  [COLOR_RGB, [1.00, 0.00, 1.00], 1.0, 'magenta'],
    6:  [COLOR_RGB, [1.00, 1.00, 0.00], 1.0, 'yellow'],
    7:  [COLOR_RGB, [1.00, 1.00, 1.00], 1.0, 'white'],
    8:  [COLOR_RGB, [0.00, 0.00, 0.56], 1.0, 'blue1'],
    9:  [COLOR_RGB, [0.00, 0.00, 0.69], 1.0, 'blue2'],
    10: [COLOR_RGB, [0.00, 0.00, 0.82], 1.0, 'blue3'],
    11: [COLOR_RGB, [0.53, 0.81, 1.00], 1.0, 'blue4'],
    12: [COLOR_RGB, [0.00, 0.56, 0.00], 1.0, 'green1'],
    13: [COLOR_RGB, [0.00, 0.69, 0.00], 1.0, 'green2'],
    14: [COLOR_RGB, [0.00, 0.82, 0.00], 1.0, 'green3'],
    15: [COLOR_RGB, [0.00, 0.56, 0.56], 1.0, 'cyan1'],
    16: [COLOR_RGB, [0.00, 0.69, 0.69], 1.0, 'cyan2'],
    17: [COLOR_RGB, [0.00, 0.82, 0.82], 1.0, 'cyan3'],
    18: [COLOR_RGB, [0.56, 0.00, 0.00], 1.0, 'red1'],
    19: [COLOR_RGB, [0.69, 0.00, 0.00], 1.0, 'red2'],
    20: [COLOR_RGB, [0.82, 0.00, 0.00], 1.0, 'red3'],
    21: [COLOR_RGB, [0.56, 0.00, 0.56], 1.0, 'magenta1'],
    22: [COLOR_RGB, [0.69, 0.00, 0.69], 1.0, 'magenta2'],
    23: [COLOR_RGB, [0.82, 0.00, 0.82], 1.0, 'magenta3'],
    24: [COLOR_RGB, [0.50, 0.19, 0.00], 1.0, 'brown1'],
    25: [COLOR_RGB, [0.63, 0.25, 0.00], 1.0, 'brown2'],
    26: [COLOR_RGB, [0.75, 0.38, 0.00], 1.0, 'brown3'],
    27: [COLOR_RGB, [1.00, 0.50, 0.50], 1.0, 'pink1'],
    28: [COLOR_RGB, [1.00, 0.63, 0.63], 1.0, 'pink2'],
    29: [COLOR_RGB, [1.00, 0.75, 0.75], 1.0, 'pink3'],
    30: [COLOR_RGB, [1.00, 0.88, 0.88], 1.0, 'pink4'],
    31: [COLOR_RGB, [1.00, 0.84, 0.00], 1.0, 'gold']
}


def color_mix(color1, color2, coef=0.5):
    rgb = cms.mix_lists(color1[1], color2[1], coef)
    a = cms.mix_vals(color1[2], color2[2], coef)
    name = cms.rgb_to_hexcolor(rgb)
    return [COLOR_RGB, rgb, a, name]
