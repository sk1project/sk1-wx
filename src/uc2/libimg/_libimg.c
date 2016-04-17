/* libimg - small module which provides binding to ImageMagick.
 *
 * Copyright (C) 2011-2012 by Igor E.Novikov
 *
 * 	This program is free software: you can redistribute it and/or modify
 *	it under the terms of the GNU General Public License as published by
 *	the Free Software Foundation, either version 3 of the License, or
 *	(at your option) any later version.
 *
 *	This program is distributed in the hope that it will be useful,
 *	but WITHOUT ANY WARRANTY; without even the implied warranty of
 *	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *	GNU General Public License for more details.
 *
 *	You should have received a copy of the GNU General Public License
 *	along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <Python.h>
#include <wand/MagickWand.h>

static PyObject *
im_InitMagick(PyObject *self, PyObject *args) {

	MagickWandGenesis();

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
im_TerminateMagick(PyObject *self, PyObject *args) {

	MagickWandTerminus();

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
im_NewImage(PyObject *self, PyObject *args) {

	MagickWand *magick_wand;

	magick_wand = NewMagickWand();

	return Py_BuildValue("O", PyCObject_FromVoidPtr((void *)magick_wand,
			(void *)DestroyMagickWand));
}

static PyObject *
im_LoadImage(PyObject *self, PyObject *args) {

	void *magick_pointer;
	MagickWand *magick_wand;
	char *filepath = NULL;
	MagickBooleanType status;

	if (!PyArg_ParseTuple(args, "Os", &magick_pointer, &filepath)){
		return Py_BuildValue("i", 0);
	}

	magick_wand = (MagickWand *) PyCObject_AsVoidPtr(magick_pointer);
	status = MagickReadImage(magick_wand, filepath);

	if (status == MagickFalse){
		return Py_BuildValue("i", 0);
	}

	return Py_BuildValue("i", 1);
}

static PyObject *
im_LoadImageBlob(PyObject *self, PyObject *args) {

	void *magick_pointer;
	MagickWand *magick_wand;
	Py_ssize_t size;
	char *blob;
	MagickBooleanType status;

	if (!PyArg_ParseTuple(args, "Os#", &magick_pointer, &blob, &size)){
		return Py_BuildValue("i", 0);
	}

	magick_wand = (MagickWand *) PyCObject_AsVoidPtr(magick_pointer);

	status = MagickReadImageBlob(magick_wand, blob, (size_t)size);

	if (status == MagickFalse){
		return Py_BuildValue("i", 0);
	}

	return Py_BuildValue("i", 1);
}

static PyObject *
im_WriteImage(PyObject *self, PyObject *args) {

	void *magick_pointer;
	MagickWand *magick_wand;
	char *filepath = NULL;
	MagickBooleanType status;

	if (!PyArg_ParseTuple(args, "Os", &magick_pointer, &filepath)){
		return Py_BuildValue("i", 0);
	}

	magick_wand = (MagickWand *) PyCObject_AsVoidPtr(magick_pointer);
	status = MagickWriteImages(magick_wand, filepath, MagickTrue);

	if (status == MagickFalse){
		return Py_BuildValue("i", 0);
	}

	return Py_BuildValue("i", 1);
}

static PyObject *
im_GetImageBlob(PyObject *self, PyObject *args) {

	void *magick_pointer;
	MagickWand *magick_wand;
	unsigned char *blob;
	size_t length;
	PyObject *ret;

	if (!PyArg_ParseTuple(args, "O", &magick_pointer)){
		return Py_BuildValue("i", 0);
	}

	magick_wand = (MagickWand *) PyCObject_AsVoidPtr(magick_pointer);
	blob = MagickGetImagesBlob(magick_wand, &length);
	ret = Py_BuildValue("s#", blob, length);
	free(blob);

	return ret;
}

static PyObject *
im_GetNumberImages(PyObject *self, PyObject *args) {

	void *magick_pointer;
	MagickWand *magick_wand;

	if (!PyArg_ParseTuple(args, "O", &magick_pointer)){
		Py_INCREF(Py_None);
		return Py_None;
	}

	magick_wand = (MagickWand *) PyCObject_AsVoidPtr(magick_pointer);

	return Py_BuildValue("i", MagickGetNumberImages(magick_wand));
}

static PyObject *
im_ResetIterator(PyObject *self, PyObject *args) {

	void *magick_pointer;
	MagickWand *magick_wand;

	if (!PyArg_ParseTuple(args, "O", &magick_pointer)){
		Py_INCREF(Py_None);
		return Py_None;
	}

	magick_wand = (MagickWand *) PyCObject_AsVoidPtr(magick_pointer);
	MagickResetIterator(magick_wand);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
im_NextImage(PyObject *self, PyObject *args) {

	void *magick_pointer;
	MagickWand *magick_wand;
	MagickBooleanType status;

	if (!PyArg_ParseTuple(args, "O", &magick_pointer)){
		Py_INCREF(Py_None);
		return Py_None;
	}

	magick_wand = (MagickWand *) PyCObject_AsVoidPtr(magick_pointer);
	status = MagickNextImage(magick_wand);

	if (status == MagickFalse){
		return Py_BuildValue("i", 0);
	}

	return Py_BuildValue("i", 1);
}


// Image types from magick/image.h
//
//	  UndefinedType,
//	  BilevelType,
//	  GrayscaleType,
//	  GrayscaleMatteType,
//	  PaletteType,
//	  PaletteMatteType,
//	  TrueColorType,
//	  TrueColorMatteType,
//	  ColorSeparationType,
//	  ColorSeparationMatteType,
//	  OptimizeType,
//	  PaletteBilevelMatteType

static PyObject *
im_GetImageType(PyObject *self, PyObject *args) {

	void *magick_pointer;
	MagickWand *magick_wand;
	ImageType img_type;

	if (!PyArg_ParseTuple(args, "O", &magick_pointer)){
		Py_INCREF(Py_None);
		return Py_None;
	}

	magick_wand = (MagickWand *) PyCObject_AsVoidPtr(magick_pointer);
	img_type = MagickGetImageType(magick_wand);

	if (img_type == BilevelType){
		return Py_BuildValue("s", "BilevelType");
	}
	else if (img_type == GrayscaleType){
		return Py_BuildValue("s", "GrayscaleType");
	}
	else if (img_type == GrayscaleMatteType){
		return Py_BuildValue("s", "GrayscaleMatteType");
	}
	else if (img_type == PaletteType){
		return Py_BuildValue("s", "PaletteType");
	}
	else if (img_type == PaletteMatteType){
		return Py_BuildValue("s", "PaletteMatteType");
	}
	else if (img_type == TrueColorType){
		return Py_BuildValue("s", "TrueColorType");
	}
	else if (img_type == TrueColorMatteType){
		return Py_BuildValue("s", "TrueColorMatteType");
	}
	else if (img_type == ColorSeparationType){
		return Py_BuildValue("s", "ColorSeparationType");
	}
	else if (img_type == ColorSeparationMatteType){
		return Py_BuildValue("s", "ColorSeparationMatteType");
	}
	else if (img_type == OptimizeType){
		return Py_BuildValue("s", "OptimizeType");
	}
	else if (img_type == PaletteBilevelMatteType){
		return Py_BuildValue("s", "PaletteBilevelMatteType");
	}
	else {
		return Py_BuildValue("s", "UndefinedType");
	}
}

// Colorspace types from magick/colorspace.h
//
//UndefinedColorspace,
//RGBColorspace,
//GRAYColorspace,
//TransparentColorspace,
//OHTAColorspace,
//LabColorspace,
//XYZColorspace,
//YCbCrColorspace,
//YCCColorspace,
//YIQColorspace,
//YPbPrColorspace,
//YUVColorspace,
//CMYKColorspace,
//sRGBColorspace,
//HSBColorspace,
//HSLColorspace,
//HWBColorspace,
//Rec601LumaColorspace,
//Rec601YCbCrColorspace,
//Rec709LumaColorspace,
//Rec709YCbCrColorspace,
//LogColorspace,
//CMYColorspace

static PyObject *
im_GetColorspace(PyObject *self, PyObject *args) {

	void *magick_pointer;
	MagickWand *magick_wand;
	ColorspaceType cs;

	if (!PyArg_ParseTuple(args, "O", &magick_pointer)){
		Py_INCREF(Py_None);
		return Py_None;
	}

	magick_wand = (MagickWand *) PyCObject_AsVoidPtr(magick_pointer);
	cs = MagickGetImageColorspace(magick_wand);

	if (cs == RGBColorspace){
		return Py_BuildValue("s", "RGBColorspace");
	}
	else if (cs == GRAYColorspace){
		return Py_BuildValue("s", "GRAYColorspace");
	}
	else if (cs == TransparentColorspace){
		return Py_BuildValue("s", "TransparentColorspace");
	}
	else if (cs == OHTAColorspace){
		return Py_BuildValue("s", "OHTAColorspace");
	}
	else if (cs == LabColorspace){
		return Py_BuildValue("s", "LabColorspace");
	}
	else if (cs == XYZColorspace){
		return Py_BuildValue("s", "XYZColorspace");
	}
	else if (cs == YCbCrColorspace){
		return Py_BuildValue("s", "YCbCrColorspace");
	}
	else if (cs == YCCColorspace){
		return Py_BuildValue("s", "YCCColorspace");
	}
	else if (cs == YIQColorspace){
		return Py_BuildValue("s", "YIQColorspace");
	}
	else if (cs == YPbPrColorspace){
		return Py_BuildValue("s", "YPbPrColorspace");
	}
	else if (cs == YUVColorspace){
		return Py_BuildValue("s", "YUVColorspace");
	}
	else if (cs == CMYKColorspace){
		return Py_BuildValue("s", "CMYKColorspace");
	}
	else if (cs == sRGBColorspace){
		return Py_BuildValue("s", "sRGBColorspace");
	}
	else if (cs == HSBColorspace){
		return Py_BuildValue("s", "HSBColorspace");
	}
	else if (cs == HSLColorspace){
		return Py_BuildValue("s", "HSLColorspace");
	}
	else if (cs == HWBColorspace){
		return Py_BuildValue("s", "HWBColorspace");
	}
	else if (cs == Rec601LumaColorspace){
		return Py_BuildValue("s", "Rec601LumaColorspace");
	}
	else if (cs == Rec601YCbCrColorspace){
		return Py_BuildValue("s", "Rec601YCbCrColorspace");
	}
	else if (cs == Rec709LumaColorspace){
		return Py_BuildValue("s", "Rec709LumaColorspace");
	}
	else if (cs == Rec709YCbCrColorspace){
		return Py_BuildValue("s", "Rec709YCbCrColorspace");
	}
	else if (cs == LogColorspace){
		return Py_BuildValue("s", "LogColorspace");
	}
	else if (cs == CMYColorspace){
		return Py_BuildValue("s", "CMYColorspace");
	}
	else {
		return Py_BuildValue("s", "UndefinedColorspace");
	}
}

static PyObject *
im_CloneImage(PyObject *self, PyObject *args) {

	void *magick_pointer;
	MagickWand *magick_wand;
	MagickWand *wand_clone;

	if (!PyArg_ParseTuple(args, "O", &magick_pointer)){
		Py_INCREF(Py_None);
		return Py_None;
	}

	magick_wand = (MagickWand *) PyCObject_AsVoidPtr(magick_pointer);
	wand_clone = CloneMagickWand(magick_wand);

	return Py_BuildValue("O", PyCObject_FromVoidPtr((void *)wand_clone,
			(void *)DestroyMagickWand));
}

static PyObject *
im_SetImageFormat(PyObject *self, PyObject *args) {

	void *magick_pointer;
	MagickWand *magick_wand;
	char *format = NULL;
	MagickBooleanType status;

	if (!PyArg_ParseTuple(args, "Os", &magick_pointer, &format)){
		return Py_BuildValue("i", 0);
	}

	magick_wand = (MagickWand *) PyCObject_AsVoidPtr(magick_pointer);
	status = MagickSetImageFormat(magick_wand, format);

	if (status == MagickFalse){
		return Py_BuildValue("i", 0);
	}

	return Py_BuildValue("i", 1);
}


ImageType
get_image_type(char* mode) {

  if (strcmp(mode, "BilevelType") == 0) {
    return BilevelType;
  }
  else if (strcmp(mode, "GrayscaleType") == 0) {
    return GrayscaleType;
  }
  else if (strcmp(mode, "GrayscaleMatteType") == 0) {
    return GrayscaleMatteType;
  }
  else if (strcmp(mode, "PaletteType") == 0) {
    return PaletteType;
  }
  else if (strcmp(mode, "PaletteMatteType") == 0) {
    return PaletteMatteType;
  }
  else if (strcmp(mode, "TrueColorType") == 0) {
    return TrueColorType;
  }
  else if (strcmp(mode, "TrueColorMatteType") == 0) {
    return TrueColorMatteType;
  }
  else if (strcmp(mode, "ColorSeparationType") == 0) {
    return ColorSeparationType;
  }
  else if (strcmp(mode, "ColorSeparationMatteType") == 0) {
    return ColorSeparationMatteType;
  }
  else {
    return TrueColorType;
  }
}

static PyObject *
im_SetImageType(PyObject *self, PyObject *args) {

	void *magick_pointer;
	MagickWand *magick_wand;
	char *img_type = NULL;

	if (!PyArg_ParseTuple(args, "Os", &magick_pointer, &img_type)){
		Py_INCREF(Py_None);
		return Py_None;
	}

	magick_wand = (MagickWand *) PyCObject_AsVoidPtr(magick_pointer);
	MagickSetImageType(magick_wand, get_image_type(img_type));

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
im_RemoveAlpaChannel(PyObject *self, PyObject *args) {

	void *magick_pointer;
	MagickWand *magick_wand;

	if (!PyArg_ParseTuple(args, "O", &magick_pointer)){
		Py_INCREF(Py_None);
		return Py_None;
	}

	magick_wand = (MagickWand *) PyCObject_AsVoidPtr(magick_pointer);
	MagickSetImageAlphaChannel(magick_wand, DeactivateAlphaChannel);

	Py_INCREF(Py_None);
	return Py_None;
}

static
PyMethodDef im_methods[] = {
		{"init_magick", im_InitMagick, METH_VARARGS},
		{"terminate_magick", im_TerminateMagick, METH_VARARGS},
		{"new_image", im_NewImage, METH_VARARGS},
		{"load_image", im_LoadImage, METH_VARARGS},
		{"load_image_blob", im_LoadImageBlob, METH_VARARGS},
		{"write_image", im_WriteImage, METH_VARARGS},
		{"get_image_blob", im_GetImageBlob, METH_VARARGS},
		{"get_number_images", im_GetNumberImages, METH_VARARGS},
		{"reset_iterator", im_ResetIterator, METH_VARARGS},
		{"next_image", im_NextImage, METH_VARARGS},
		{"get_image_type", im_GetImageType, METH_VARARGS},
		{"get_colorspace", im_GetColorspace, METH_VARARGS},
		{"clone_image", im_CloneImage, METH_VARARGS},
		{"set_image_format", im_SetImageFormat, METH_VARARGS},
		{"set_image_type", im_SetImageType, METH_VARARGS},
		{"remove_alpha_channel", im_RemoveAlpaChannel, METH_VARARGS},

	{NULL, NULL}
};

void
init_libimg(void)
{
    Py_InitModule("_libimg", im_methods);
}
