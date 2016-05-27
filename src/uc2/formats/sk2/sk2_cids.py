# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011-2015 by Igor E. Novikov
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

from uc2 import _

# Document object enumeration
DOCUMENT = 1

METAINFO = 10
STYLES = 11
STYLE = 12
PROFILES = 13
PROFILE = 14
FONTS = 15
FONT = 16
IMAGES = 17
IMAGE = 18

STRUCTURAL_CLASS = 50
PAGES = 51
PAGE = 52
LAYER_GROUP = 53
MASTER_LAYERS = 54
LAYER = 55
GRID_LAYER = 57
GUIDE_LAYER = 58
DESKTOP_LAYERS = 59
GUIDE = 60

SELECTABLE_CLASS = 100
COMPOUND_CLASS = 101
GROUP = 102
CONTAINER = 103
TP_GROUP = 104

PRIMITIVE_CLASS = 200
RECTANGLE = 201
CIRCLE = 202
POLYGON = 203
CURVE = 204
TEXT_BLOCK = 205
TEXT_COLUMN = 206

BITMAP_CLASS = 250
PIXMAP = 251

CID_TO_NAME = {
	DOCUMENT: _('Document'),

	METAINFO: _('Metainfo'), STYLES: _('Styles'), STYLE: _('Style'),
	PROFILES: _('Profiles'), PROFILE: _('Profile'), FONTS: _('Fonts'),
	FONT: _('Font'), IMAGES: _('Images'), IMAGE: _('Image'),

	PAGES: _('Pages'), PAGE: _('Page'), LAYER_GROUP: _('Layer group'),
	MASTER_LAYERS: _('Master layers'), LAYER: _('Layer'),
	GRID_LAYER: _('Grid layer'), GUIDE_LAYER: _('Guide layer'),
	DESKTOP_LAYERS: _('Desktop layers'), GUIDE: _('Guide'),

	GROUP: _('Group'), CONTAINER: _('Container'),
	TP_GROUP: _('Text on Path Group'),

	RECTANGLE: _('Rectangle'), CIRCLE: _('Ellipse'),
	POLYGON: _('Polygon'), CURVE: _('Curve'),
	TEXT_BLOCK: _('Text block'), TEXT_COLUMN: _('Text column'),
	PIXMAP: _('Bitmap'),
	}


CID_TO_TAGNAME = {
	DOCUMENT: 'Document',

	METAINFO: 'Metainfo', STYLES: 'Styles', STYLE: 'Style',
	PROFILES: 'Profiles', PROFILE: 'Profile', FONTS: 'Fonts',
	FONT: 'Font', IMAGES: 'Images', IMAGE: 'Image',

	PAGES: 'Pages', PAGE: 'Page', LAYER_GROUP: 'LayerGroup',
	MASTER_LAYERS: 'MasterLayers', LAYER: 'Layer',
	GRID_LAYER: 'GridLayer', GUIDE_LAYER: 'GuideLayer',
	DESKTOP_LAYERS: 'DesktopLayers', GUIDE: 'Guide',

	GROUP: 'Group', CONTAINER: 'Container',
	TP_GROUP: 'TP_Group',

	RECTANGLE: 'Rectangle', CIRCLE: 'Ellipse',
	POLYGON: 'Polygon', CURVE: 'Curve',
	TEXT_BLOCK: 'TextBlock', TEXT_COLUMN: 'TextColumn',
	PIXMAP: 'Pixmap',
	}

TAGNAME_TO_CID = {
	'Document': DOCUMENT,

	'Metainfo': METAINFO, 'Styles': STYLES, 'Style': STYLE,
	'Profiles': PROFILES, 'Profile': PROFILE, 'Fonts': FONTS,
	'Font': FONT, 'Images': IMAGES, 'Image': IMAGE,

	'Pages': PAGES, 'Page': PAGE, 'LayerGroup': LAYER_GROUP,
	'MasterLayers': MASTER_LAYERS, 'Layer': LAYER,
	'GridLayer': GRID_LAYER, 'GuideLayer': GUIDE_LAYER,
	'DesktopLayers': DESKTOP_LAYERS, 'Guide': GUIDE,

	'Group': GROUP, 'Container': CONTAINER,
	'TP_Group': TP_GROUP,

	'Rectangle': RECTANGLE, 'Ellipse': CIRCLE,
	'Polygon': POLYGON, 'Curve': CURVE,
	'TextBlock': TEXT_BLOCK, 'TextColumn': TEXT_COLUMN,
	'Pixmap': PIXMAP,
	}
