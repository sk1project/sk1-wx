# -*- coding: utf-8 -*-
#
#  cms - module which provides binding to LittleCMS2 library.
#
#  Copyright (C) 2012-2018 by Igor E. Novikov
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

import os
from PIL import Image

import _cms

from uc2 import uc2const


class CmsError(Exception):
    pass


def get_version():
    """Returns LCMS version.

    :rtype str
    :return: version string
    """
    ver = str(_cms.getVersion())
    return '%s.%s' % (ver[0], ver[2]) if ver[0] == '2' \
        else '%s.%s' % (ver[0], ver[1:])


COLOR_RNG = range(256)


def cms_set_alarm_codes(r, g, b):
    """Used to define gamut check marker.
    r,g,b are expected to be integers in range 0..255

    :param r: red channel
    :param g: green channel
    :param b: blue channel
    """
    if r in COLOR_RNG and g in COLOR_RNG and b in COLOR_RNG:
        _cms.setAlarmCodes(r, g, b)
    else:
        raise CmsError('r,g,b are expected to be integers in range 0..255')


def cms_open_profile_from_file(profile_path):
    """Returns a handle to lcms profile wrapped as a Python object.
    The handle doesn't require to be closed after usage because
    on object delete operation Python calls native cms_close_profile()
    function automatically

    :param profile_path: a valid filename path to the ICC profile
    :return: handle to lcms profile
    """
    if not os.path.isfile(profile_path):
        raise CmsError('Invalid profile path provided: %s' % profile_path)

    result = _cms.openProfile(profile_path)

    if result is None:
        msg = 'It seems provided profile is invalid'
        raise CmsError(msg + ': %s' % profile_path)

    return result


def cms_open_profile_from_string(profile_str):
    """Returns a handle to lcms profile wrapped as a Python object.
    The handle doesn't require to be closed after usage because
    on object delete operation Python calls native cms_close_profile()
    function automatically.

    :param profile_str: ICC profile as a python string
    :return: handle to lcms profile
    """

    if not len(profile_str):
        raise CmsError("Empty profile string provided")

    result = _cms.openProfileFromString(profile_str)

    if result is None:
        raise CmsError('It seems provided profile string is invalid!')

    return result


def cms_create_srgb_profile():
    """Artificial functionality. The function emulates built-in sRGB
    profile reading profile resource attached to the package.
    Returns a handle to lcms built-in sRGB profile wrapped as a Python object.
    The handle doesn't require to be closed after usage because
    on object delete operation Python calls native cms_close_profile()
    function automatically

    :return: handle to lcms built-in sRGB profile
    """
    import srgb_profile_rc
    profile = srgb_profile_rc.get_resource(True)
    return cms_open_profile_from_file(profile.name)


def get_srgb_profile_resource():
    """Returns named temporary file object of built-in sRGB profile.

    :return: path to sRGB profile
    """
    import srgb_profile_rc
    return srgb_profile_rc.get_resource(True)


def save_srgb_profile(path):
    """Saves content of built-in sRGB profile.

    :param path: sRGB profile path as a string
    """
    import srgb_profile_rc
    srgb_profile_rc.save_resource(path)


def cms_create_cmyk_profile():
    """Artificial functionality. The function emulates built-in CMYK
    profile reading profile resource attached to the package.
    Returns a handle to lcms built-in CMYK profile wrapped as a Python object.
    The handle doesn't require to be closed after usage because
    on object delete operation Python calls native cms_close_profile()
    function automatically

    :return: handle to lcms built-in CMYK profile
    """
    import cmyk_profile_rc
    profile = cmyk_profile_rc.get_resource(True)
    return cms_open_profile_from_file(profile.name)


def get_cmyk_profile_resource():
    """Returns named temporary file object of built-in CMYK profile.

    :return: path to built-in CMYK profile
    """
    import cmyk_profile_rc
    return cmyk_profile_rc.get_resource(True)


def save_cmyk_profile(path):
    """Saves content of built-in CMYK profile.

    :param path: CMYK profile path as a string
    """
    import cmyk_profile_rc
    cmyk_profile_rc.save_resource(path)


def cms_create_display_profile():
    """Artificial functionality. The function emulates built-in display
    profile reading profile resource attached to the package.
    Returns a handle to lcms built-in display profile wrapped
    as a Python object.
     
    The handle doesn't require to be closed after usage because
    on object delete operation Python calls native cms_close_profile()
    function automatically

    :return: handle to lcms built-in display profile
    """
    import display_profile_rc
    profile = display_profile_rc.get_resource(True)
    return cms_open_profile_from_file(profile.name)


def get_display_profile_resource():
    """Returns named temporary file object of built-in display profile.

    :return: path to built-in display profile
    """
    import display_profile_rc
    return display_profile_rc.get_resource(True)


def save_display_profile(path):
    """Saves content of built-in display profile.

    :param path: display profile path as a string
    """
    import display_profile_rc
    display_profile_rc.save_resource(path)


def cms_create_lab_profile():
    """Artificial functionality. The function emulates built-in Lab
    profile reading profile resource attached to the package.
    Returns a handle to lcms built-in Lab profile wrapped as a Python object. 
    The handle doesn't require to be closed after usage because
    on object delete operation Python calls native cms_close_profile()
    function automatically

    :return: handle to lcms built-in display profile
    """
    import lab_profile_rc
    profile = lab_profile_rc.get_resource(True)
    return cms_open_profile_from_file(profile.name)


def get_lab_profile_resource():
    """Returns named temporary file object of built-in Lab profile.

    :return: path to built-in Lab profile
    """
    import lab_profile_rc
    return lab_profile_rc.get_resource(True)


def save_lab_profile(path):
    """Saves content of built-in Lab profile.

    :param path: Lab profile path as a string
    """
    import lab_profile_rc
    lab_profile_rc.save_resource(path)


def cms_create_gray_profile():
    """Artificial functionality. The function emulates built-in Gray
    profile reading profile resource attached to the package.
    Returns a handle to lcms built-in Gray profile wrapped as a Python object. 
    The handle doesn't require to be closed after usage because
    on object delete operation Python calls native cms_close_profile()
    function automatically

    :return: handle to lcms built-in Gray profile
    """
    import gray_profile_rc
    profile = gray_profile_rc.get_resource(True)
    return cms_open_profile_from_file(profile.name)


def get_gray_profile_resource():
    """Returns named temporary file object of built-in Gray profile.

    :return: path to built-in Gray profile
    """
    import gray_profile_rc
    return gray_profile_rc.get_resource(True)


def save_gray_profile(path):
    """Saves content of built-in Gray profile.

    :param path: Gray profile path as a string
    """
    import gray_profile_rc
    gray_profile_rc.save_resource(path)


FUNC_MAP = {
    uc2const.COLOR_RGB: (cms_create_srgb_profile,
                         get_srgb_profile_resource,
                         save_srgb_profile),
    uc2const.COLOR_CMYK: (cms_create_cmyk_profile,
                          get_cmyk_profile_resource,
                          save_cmyk_profile),
    uc2const.COLOR_LAB: (cms_create_lab_profile,
                         get_lab_profile_resource,
                         save_lab_profile),
    uc2const.COLOR_GRAY: (cms_create_gray_profile,
                          get_gray_profile_resource,
                          save_gray_profile),
    uc2const.COLOR_DISPLAY: (cms_create_display_profile,
                             get_display_profile_resource,
                             save_display_profile),
}


def cms_create_default_profile(colorspace):
    """Artificial functionality. The function emulates built-in
    profile reading according profile resource attached to the package.
    Returns a handle to lcms built-in profile wrapped as a Python object.
    The handle doesn't require to be closed after usage because
    on object delete operation Python calls native cms_close_profile()
    function automatically

    :param colorspace: colorspace constant
    :return: handle to lcms profile or None
    """
    profile = FUNC_MAP.get(colorspace, None)
    return None if profile is None else profile[0]()


def cms_get_default_profile_resource(colorspace):
    """Artificial functionality.
    Returns temporary named file object.

    :param colorspace: colorspace constant
    :return: path to built-in profile
    """
    profile = FUNC_MAP.get(colorspace, None)
    return None if profile is None else profile[1]()


def cms_save_default_profile(path, colorspace):
    """Artificial functionality.
    Saves content of built-in specified profile.

    :param path: profile path as a string
    :param colorspace: colorspace constant
    """
    profile = FUNC_MAP.get(colorspace, None)
    if profile is not None:
        profile[2](path)
    else:
        raise CmsError('Unexpected colorspace requested %s' % str(colorspace))


INTENTS = (0, 1, 2, 3)


def cms_create_transform(in_profile, in_mode, out_profile, out_mode,
                         intent=uc2const.INTENT_PERCEPTUAL,
                         flags=uc2const.cmsFLAGS_NOTPRECALC):
    """Returns a handle to lcms transformation wrapped as a Python object.

    :param in_profile: valid lcms profile handle
    :param in_mode: valid lcms profile handle
    :param out_profile: valid lcms or PIL mode
    :param out_mode: valid lcms or PIL mode
    :param intent: integer constant (0-3) of transform rendering intent
    :param flags: lcms flags

    :return: handle to lcms transformation
    """

    if intent not in INTENTS:
        raise CmsError('renderingIntent must be an integer between 0 and 3')

    result = _cms.buildTransform(in_profile, in_mode, out_profile, out_mode,
                                 intent, flags)

    if result is None:
        msg = 'Cannot create requested transform'
        raise CmsError("%s: %s %s" % (msg, in_mode, out_mode))

    return result


def cms_create_proofing_transform(in_profile, in_mode, out_profile, out_mode,
                                  proof_profile,
                                  intent=uc2const.INTENT_PERCEPTUAL,
                                  pintent=uc2const.INTENT_RELATIVE_COLORIMETRIC,
                                  flags=uc2const.cmsFLAGS_SOFTPROOFING):
    """Returns a handle to lcms transformation wrapped as a Python object.

    :param in_profile: valid lcms profile handle
    :param in_mode: valid lcms or PIL mode
    :param out_profile: valid lcms profile handle
    :param out_mode: valid lcms or PIL mode
    :param proof_profile: valid lcms profile handle
    :param intent: integer constant (0-3) of transform rendering intent
    :param pintent: integer constant (0-3) of transform proofing intent
    :param flags: lcms flags

    :return: handle to lcms transformation
    """

    if intent not in INTENTS:
        raise CmsError('Rendering intent must be an integer between 0 and 3')

    if pintent not in INTENTS:
        raise CmsError('Proofing intent must be an integer between 0 and 3')

    result = _cms.buildProofingTransform(in_profile, in_mode,
                                         out_profile, out_mode,
                                         proof_profile, intent,
                                         pintent, flags)

    if result is None:
        msg = 'Cannot create requested proofing transform'
        raise CmsError("%s: %s %s" % (msg, in_mode, out_mode))

    return result


def cms_do_transform(transform, inbuff, outbuff):
    """Transform color values from inputBuffer to outputBuffer using provided
    lcms transform handle.

    :param transform: valid lcms transformation handle
    :param inbuff: 4-member list. The members should be between 0 and 255
    :param outbuff: 4-member list. The members should be between 0 and 255
    """
    if isinstance(inbuff, list) and isinstance(outbuff, list):
        ret = _cms.transformPixel(transform, *inbuff)
        outbuff[0] = ret[0]
        outbuff[1] = ret[1]
        outbuff[2] = ret[2]
        outbuff[3] = ret[3]
        return
    else:
        msg = 'inbuff and outbuff must be Python 4-member list objects'
        raise CmsError(msg)


def cms_do_bitmap_transform(transform, image, in_mode, out_mode):
    """Provides PIL images support for color management.
    Currently supports L, RGB, CMYK and LAB modes only.

    :param transform: valid lcms transformation handle
    :param image: valid PIL image object
    :param in_mode: valid lcms or PIL mode
    :param out_mode: valid lcms or PIL mode

    :return: new PIL image object in out_mode colorspace
    """

    if image.mode not in uc2const.IMAGE_COLORSPACES:
        raise CmsError('Unsupported image type: %s' % image.mode)

    if in_mode not in uc2const.IMAGE_COLORSPACES:
        raise CmsError('Unsupported in_mode type: %s' % in_mode)

    if out_mode not in uc2const.IMAGE_COLORSPACES:
        raise CmsError('unsupported out_mode type: %s' % out_mode)

    w, h = image.size
    image.load()
    new_image = Image.new(out_mode, (w, h))

    _cms.transformBitmap(transform, image.im, new_image.im, w, h)

    return new_image


def cms_get_profile_name(profile):
    """Returns profile name

    :param profile: valid lcms profile handle
    :return: profile name string
    """
    return _cms.getProfileName(profile).strip().decode('cp1252').encode('utf-8')


def cms_get_profile_info(profile):
    """Returns profile description info

    :param profile: valid lcms profile handle
    :return: profile description info string
    """
    return _cms.getProfileInfo(profile).strip().decode('cp1252').encode('utf-8')


def cms_get_profile_copyright(profile):
    """Returns profile copyright info

    :param profile: valid lcms profile handle
    :return: profile copyright info string
    """
    return _cms.getProfileInfoCopyright(profile).strip().decode('cp1252').encode('utf-8')
