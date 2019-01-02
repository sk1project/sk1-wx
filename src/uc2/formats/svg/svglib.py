# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Igor E. Novikov
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
import math
import re
from copy import deepcopy

from uc2 import uc2const, libgeom, cms, sk2const
from uc2.formats.svg import svg_colors
from uc2.formats.xml_.xml_model import XMLObject, XmlContentText
from uc2.libgeom import add_points, sub_points, mult_point

PATH_STUB = [[], [], sk2const.CURVE_OPENED]
F13 = 1.0 / 3.0
F23 = 2.0 / 3.0
LOG = logging.getLogger(__name__)


def check_svg_attr(svg_obj, attr, value=None):
    if value is None: return attr in svg_obj.attrs
    if attr in svg_obj.attrs and svg_obj.attrs[attr] == value:
        return True
    return False


def trafo_skewX(grad=0.0):
    angle = math.pi * grad / 180.0
    return [1.0, 0.0, math.tan(angle), 1.0, 0.0, 0.0]


def trafo_skewY(grad=0.0):
    angle = math.pi * grad / 180.0
    return [1.0, math.tan(angle), 0.0, 1.0, 0.0, 0.0]


def trafo_rotate(grad, cx=0.0, cy=0.0):
    return libgeom.trafo_rotate_grad(grad, cx, cy)


def trafo_scale(m11, m22=None):
    if m22 is None: m22 = m11
    return [m11, 0.0, 0.0, m22, 0.0, 0.0]


def trafo_translate(dx, dy=0.0):
    LOG.debug('translate %s', [1.0, 0.0, 0.0, 1.0, dx, dy])
    return [1.0, 0.0, 0.0, 1.0, dx, dy]


def trafo_matrix(m11, m21, m12, m22, dx, dy):
    return [m11, m21, m12, m22, dx, dy]


def get_svg_trafo(strafo):
    trafo = [] + libgeom.NORMAL_TRAFO
    trs = strafo.split(') ')
    trs.reverse()
    for tr in trs:
        tr += ')'
        tr = tr.replace(', ', ',').replace(' ', ',').replace('))', ')')
        try:
            code = compile('tr=trafo_' + tr, '<string>', 'exec')
            exec code
        except:
            continue
        trafo = libgeom.multiply_trafo(trafo, tr)
    return trafo


def get_svg_level_trafo(svg_obj, trafo):
    tr = [] + libgeom.NORMAL_TRAFO
    if svg_obj.tag == 'use':
        if 'x' in svg_obj.attrs:
            tr[4] += float(svg_obj.attrs['x'])
        if 'y' in svg_obj.attrs:
            tr[5] += float(svg_obj.attrs['y'])
    if 'transform' in svg_obj.attrs:
        tr1 = get_svg_trafo(svg_obj.attrs['transform'])
        tr = libgeom.multiply_trafo(tr, tr1)
    tr = libgeom.multiply_trafo(tr, trafo)
    return tr


def parse_svg_points(spoints):
    points = []
    spoints = re.sub('  *', ' ', spoints)
    spoints = spoints.replace('-', ',-').replace('e,-', 'e-')
    spoints = spoints.replace(', ,', ',').replace(' ', ',')
    pairs = spoints.replace(',,', ',').split(',')
    if not pairs[0]: pairs = pairs[1:]
    pairs = [pairs[i:i + 2] for i in range(0, len(pairs), 2)]
    for pair in pairs:
        try:
            points.append([float(pair[0]), float(pair[1])])
        except:
            continue
    return points


def parse_svg_coords(scoords):
    scoords = scoords.strip().replace(',', ' ').replace('-', ' -')
    scoords = scoords.replace('e -', 'e-').strip()
    scoords = re.sub('  *', ' ', scoords)
    if scoords:
        processed_items = []
        for item in scoords.split(' '):
            count = item.count('.')
            if count > 1:
                subitems = item.rsplit('.', count - 1)
                processed_items.append(subitems[0])
                processed_items += ['.' + s for s in subitems[1:]]
            else:
                processed_items.append(item)
        return [float(item) for item in processed_items]
    return None


def parse_svg_color(sclr, alpha=1.0, current_color=''):
    clr = deepcopy(svg_colors.SVG_COLORS['black'])
    clr[2] = alpha
    if sclr == 'currentColor' and current_color:
        sclr = current_color
    if sclr[0] == '#':
        if 'icc-color' in sclr:
            vals = sclr.split('icc-color(')[1].replace(')', '').split(',')
            if len(vals) == 5:
                color_vals = []
                try:
                    color_vals = [float(x) for x in vals[1:]]
                except:
                    pass
                if color_vals and len(color_vals) == 4:
                    return [uc2const.COLOR_CMYK, color_vals, alpha, '']
        elif 'device-cmyk' in sclr:
            vals = sclr.split('device-cmyk(')[1].replace(')', '').split(',')
            if len(vals) in (3, 4):
                color_vals = []
                try:
                    color_vals = [float(x) for x in vals[1:]]
                except:
                    pass
                if color_vals and len(color_vals) in (3, 4):
                    if len(color_vals) == 3: color_vals.append(0.0)
                    return [uc2const.COLOR_CMYK, color_vals, alpha, '']

        sclr = sclr.split(' ')[0]
        try:
            vals = cms.hexcolor_to_rgb(sclr)
            clr = [uc2const.COLOR_RGB, vals, alpha, '']
        except:
            pass
    elif sclr[:4] == 'rgb(':
        vals = sclr[4:].split(')')[0].split(',')
        if len(vals) == 3:
            decvals = []
            for val in vals:
                val = val.strip()
                if '%' in val:
                    decval = float(val.replace('%', ''))
                    if decval > 100.0: decval = 100.0
                    if decval < 0.0: decval = 0.0
                    decval = decval / 100.0
                else:
                    decval = float(val)
                    if decval > 255.0: decval = 255.0
                    if decval < 0.0: decval = 0.0
                    decval = decval / 255.0
                decvals.append(decval)
            clr = [uc2const.COLOR_RGB, decvals, alpha, '']
    else:
        if sclr in svg_colors.SVG_COLORS:
            clr = deepcopy(svg_colors.SVG_COLORS[sclr])
            clr[2] = alpha
    return clr


def base_point(point):
    if len(point) == 2: return [] + point
    return [] + point[-1]


def parse_svg_path_cmds(pathcmds):
    index = 0
    last = None
    last_index = 0
    cmds = []
    pathcmds = re.sub('  *', ' ', pathcmds)
    for item in pathcmds:
        if item in 'MmZzLlHhVvCcSsQqTtAa':
            if last:
                coords = parse_svg_coords(pathcmds[last_index + 1:index])
                cmds.append((last, coords))
            last = item
            last_index = index
        index += 1

    coords = parse_svg_coords(pathcmds[last_index + 1:index])
    cmds.append([last, coords])

    paths = []
    path = []
    cpoint = []
    rel_flag = False
    last_cmd = 'M'
    last_quad = None

    for cmd in cmds:
        if cmd[0] in 'Mm':
            if path: paths.append(path)
            path = deepcopy(PATH_STUB)
            rel_flag = cmd[0] == 'm'
            points = [cmd[1][i:i + 2] for i in range(0, len(cmd[1]), 2)]
            for point in points:
                if cpoint and rel_flag:
                    point = add_points(base_point(cpoint), point)
                if not path[0]:
                    path[0] = point
                else:
                    path[1].append(point)
                cpoint = point
        elif cmd[0] in 'Zz':
            p0 = [] + base_point(cpoint)
            p1 = [] + path[0]
            if not libgeom.is_equal_points(p0, p1, 8):
                path[1].append([] + path[0])
            path[2] = sk2const.CURVE_CLOSED
            cpoint = [] + path[0]
        elif cmd[0] in 'Cc':
            rel_flag = cmd[0] == 'c'
            points = [cmd[1][i:i + 2] for i in range(0, len(cmd[1]), 2)]
            points = [points[i:i + 3] for i in range(0, len(points), 3)]
            for point in points:
                if rel_flag:
                    point = [add_points(base_point(cpoint), point[0]),
                        add_points(base_point(cpoint), point[1]),
                        add_points(base_point(cpoint), point[2])]
                qpoint = [] + point
                qpoint.append(sk2const.NODE_CUSP)
                path[1].append(qpoint)
                cpoint = point
        elif cmd[0] in 'Ll':
            rel_flag = cmd[0] == 'l'
            points = [cmd[1][i:i + 2] for i in range(0, len(cmd[1]), 2)]
            for point in points:
                if rel_flag:
                    point = add_points(base_point(cpoint), point)
                path[1].append(point)
                cpoint = point
        elif cmd[0] in 'Hh':
            rel_flag = cmd[0] == 'h'
            for x in cmd[1]:
                dx, y = base_point(cpoint)
                if rel_flag:
                    point = [x + dx, y]
                else:
                    point = [x, y]
                path[1].append(point)
                cpoint = point
        elif cmd[0] in 'Vv':
            rel_flag = cmd[0] == 'v'
            for y in cmd[1]:
                x, dy = base_point(cpoint)
                if rel_flag:
                    point = [x, y + dy]
                else:
                    point = [x, y]
                path[1].append(point)
                cpoint = point
        elif cmd[0] in 'Ss':
            rel_flag = cmd[0] == 's'
            points = [cmd[1][i:i + 2] for i in range(0, len(cmd[1]), 2)]
            points = [points[i:i + 2] for i in range(0, len(points), 2)]
            for point in points:
                q = cpoint
                p = cpoint
                if len(cpoint) > 2:
                    q = cpoint[1]
                    p = cpoint[2]
                p1 = sub_points(add_points(p, p), q)
                if rel_flag:
                    p2 = add_points(base_point(cpoint), point[0])
                    p3 = add_points(base_point(cpoint), point[1])
                else:
                    p2, p3 = point
                point = [p1, p2, p3]
                qpoint = [] + point
                qpoint.append(sk2const.NODE_CUSP)
                path[1].append(qpoint)
                cpoint = point

        elif cmd[0] in 'Qq':
            rel_flag = cmd[0] == 'q'
            groups = [cmd[1][i:i + 4] for i in range(0, len(cmd[1]), 4)]
            for vals in groups:
                p = base_point(cpoint)
                if rel_flag:
                    q = add_points(p, [vals[0], vals[1]])
                    p3 = add_points(p, [vals[2], vals[3]])
                else:
                    q = [vals[0], vals[1]]
                    p3 = [vals[2], vals[3]]
                p1 = add_points(mult_point(p, F13), mult_point(q, F23))
                p2 = add_points(mult_point(p3, F13), mult_point(q, F23))

                point = [p1, p2, p3]
                qpoint = [] + point
                qpoint.append(sk2const.NODE_CUSP)
                path[1].append(qpoint)
                cpoint = point
                last_quad = q

        elif cmd[0] in 'Tt':
            rel_flag = cmd[0] == 't'
            groups = [cmd[1][i:i + 2] for i in range(0, len(cmd[1]), 2)]
            if last_cmd not in 'QqTt' or last_quad is None:
                last_quad = base_point(cpoint)
            for vals in groups:
                p = base_point(cpoint)
                q = sub_points(mult_point(p, 2.0), last_quad)
                if rel_flag:
                    p3 = add_points(p, [vals[0], vals[1]])
                else:
                    p3 = [vals[0], vals[1]]
                p1 = add_points(mult_point(p, F13), mult_point(q, F23))
                p2 = add_points(mult_point(p3, F13), mult_point(q, F23))

                point = [p1, p2, p3]
                qpoint = [] + point
                qpoint.append(sk2const.NODE_CUSP)
                path[1].append(qpoint)
                cpoint = point
                last_quad = q

        elif cmd[0] in 'Aa':
            rel_flag = cmd[0] == 'a'
            arcs = [cmd[1][i:i + 7] for i in range(0, len(cmd[1]), 7)]

            for arc in arcs:
                cpoint = base_point(cpoint)
                rev_flag = False
                rx, ry, xrot, large_arc_flag, sweep_flag, x, y = arc
                rx = abs(rx)
                ry = abs(ry)
                if rel_flag:
                    x += cpoint[0]
                    y += cpoint[1]
                if cpoint == [x, y]: continue
                if not rx or not ry:
                    path[1].append([x, y])
                    continue

                vector = [[] + cpoint, [x, y]]
                if sweep_flag:
                    vector = [[x, y], [] + cpoint]
                    rev_flag = True
                cpoint = [x, y]

                dir_tr = libgeom.trafo_rotate_grad(-xrot)

                if rx > ry:
                    tr = [1.0, 0.0, 0.0, rx / ry, 0.0, 0.0]
                    r = rx
                else:
                    tr = [ry / rx, 0.0, 0.0, 1.0, 0.0, 0.0]
                    r = ry

                dir_tr = libgeom.multiply_trafo(dir_tr, tr)
                vector = libgeom.apply_trafo_to_points(vector, dir_tr)

                l = libgeom.distance(*vector)

                if l > 2.0 * r: r = l / 2.0

                mp = libgeom.midpoint(*vector)

                tr0 = libgeom.trafo_rotate(math.pi / 2.0, mp[0], mp[1])
                pvector = libgeom.apply_trafo_to_points(vector, tr0)

                k = math.sqrt(r * r - l * l / 4.0)
                if large_arc_flag:
                    center = libgeom.midpoint(mp,
                        pvector[1], 2.0 * k / l)
                else:
                    center = libgeom.midpoint(mp,
                        pvector[0], 2.0 * k / l)

                angle1 = libgeom.get_point_angle(vector[0], center)
                angle2 = libgeom.get_point_angle(vector[1], center)

                da = angle2 - angle1
                start = angle1
                end = angle2
                if large_arc_flag:
                    if -math.pi >= da or da <= math.pi:
                        start = angle2
                        end = angle1
                        rev_flag = not rev_flag
                else:
                    if -math.pi <= da or da >= math.pi:
                        start = angle2
                        end = angle1
                        rev_flag = not rev_flag

                pth = libgeom.get_circle_paths(start, end,
                    sk2const.ARC_ARC)[0]

                if rev_flag:
                    pth = libgeom.reverse_path(pth)

                points = pth[1]
                for point in points:
                    if len(point) == 3:
                        point.append(sk2const.NODE_CUSP)

                tr0 = [1.0, 0.0, 0.0, 1.0, -0.5, -0.5]
                points = libgeom.apply_trafo_to_points(points, tr0)

                tr1 = [2.0 * r, 0.0, 0.0, 2.0 * r, 0.0, 0.0]
                points = libgeom.apply_trafo_to_points(points, tr1)

                tr2 = [1.0, 0.0, 0.0, 1.0, center[0], center[1]]
                points = libgeom.apply_trafo_to_points(points, tr2)

                tr3 = libgeom.invert_trafo(dir_tr)
                points = libgeom.apply_trafo_to_points(points, tr3)

                for point in points:
                    path[1].append(point)

        last_cmd = cmd[0]

    if path: paths.append(path)
    return paths


def parse_svg_stops(stops, current_color):
    sk2_stops = []
    for stop in stops:
        if not stop.tag == 'stop': continue
        offset = stop.attrs['offset']
        if offset[-1] == '%':
            offset = float(offset[:-1]) / 100.0
        else:
            offset = float(offset)

        alpha = 1.0
        sclr = 'black'
        if 'stop-opacity' in stop.attrs:
            alpha = float(stop.attrs['stop-opacity'])
        if 'stop-color' in stop.attrs:
            sclr = stop.attrs['stop-color']

        if 'style' in stop.attrs:
            style = {}
            stls = stop.attrs['style'].split(';')
            for stl in stls:
                vals = stl.split(':')
                if len(vals) == 2:
                    style[vals[0].strip()] = vals[1].strip()
            if 'stop-opacity' in style:
                alpha = float(style['stop-opacity'])
            if 'stop-color' in style:
                sclr = style['stop-color'].strip()

        clr = parse_svg_color(sclr, alpha, current_color)
        sk2_stops.append([offset, clr])
    return sk2_stops


def parse_svg_text(objs):
    ret = ''
    for obj in objs:
        if obj.is_content():
            text = obj.text.replace('\n', '').replace('\r', '')
            ret += re.sub('  *', ' ', text)
        elif obj.childs:
            ret += parse_svg_text(obj.childs)
            if 'sodipodi:role' in obj.attrs and \
                            obj.attrs['sodipodi:role'].strip() == 'line':
                ret += '\n'
    ret = ret.lstrip()
    if ret and ret[-1] == '\n': ret = ret[:-1]
    return ret


def create_xmlobj(tag, attrs={}):
    obj = XMLObject(tag)
    if attrs: obj.attrs = attrs
    return obj


def create_nl():
    return create_spacer()


def create_spacer(txt='\n'):
    return XmlContentText(txt)


def create_rect(x, y, w, h):
    attrs = {
        'x': str(x),
        'y': str(y),
        'width': str(w),
        'height': str(h)
    }
    return create_xmlobj('rect', attrs)


def translate_style_dict(style):
    ret = ''
    for item in style.keys():
        ret += '%s:%s;' % (item, style[item])
    return ret


def point_to_str(point):
    return ' %s,%s' % (str(round(point[0], 4)), str(round(point[1], 4)))


def translate_paths_to_d(paths):
    ret = ''
    for path in paths:
        cmd = 'M'
        ret += ' M' + point_to_str(path[0])
        for item in path[1]:
            if len(item) == 2:
                if not cmd == 'L':
                    cmd = 'L'
                    ret += ' L'
                ret += point_to_str(item)
            else:
                if not cmd == 'C':
                    cmd = 'C'
                    ret += ' C'
                ret += point_to_str(item[0])
                ret += point_to_str(item[1])
                ret += point_to_str(item[2])
        if path[2] == sk2const.CURVE_CLOSED:
            ret += ' Z'
    return ret.strip()
