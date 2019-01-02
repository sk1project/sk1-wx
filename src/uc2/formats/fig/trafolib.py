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

import math


def norm(a, b):
    return a * a + b * b


def normalize(a, b):
    scale = math.sqrt(norm(a, b))
    return a / scale, b / scale


def determinant(trafo):
    ''' Finds determinant of the trafo.
    '''
    return trafo[0] * trafo[3] - trafo[1] * trafo[2]


def trafo_split(trafo):
    # translation
    m11, m21, m12, m22, dx, dy = trafo

    # scale and shear
    scale_x = math.sqrt(norm(m11, m21))
    if determinant(trafo) < 0:
        scale_x = -scale_x

    nm11, nm21 = normalize(m11, m21)
    shear = nm11 * m12 + nm21 * m22

    nm12, nm22 = m12 - nm11 * shear, m22 - nm21 * shear
    scale_y = math.sqrt(norm(nm12, nm22))
    nm12, nm22 = normalize(nm12, nm22)

    shear = shear / scale_y

    # rotation
    if nm22 < 0:
        angle = math.acos(nm22)
        if nm21 < 0:
            angle = math.pi - angle
    else:
        angle = math.asin(nm21) + math.pi

    return dict(
        dx=dx, dy=dy, scale_x=scale_x, scale_y=scale_y,
        rotate=angle, shear=shear
    )
