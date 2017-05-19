'''
Created on 8 mai 2017

@author: gabri
'''
from __future__ import division, print_function, absolute_import
import numpy 
import tempfile

from numpy import (amin,amax, ravel, asarray, cast, arange, ones, newaxis, transpose, iscomplexobj,
                    uint8, issubdtype, array)


from PIL.Image import Image
import PIL.ImageFilter
from tensorflow.python.summary.summary import image
from builtins import str



if not hasattr(Image, 'frombytes'):
    Image.frombytes = Image.fromstring

__all__ = ['fromimage', 'toimage', 'imsave', 'imread', 'bytescale',
           'imrotate', 'imresize', 'imshow', 'imfilter']

#return a byte-scaled Image

def bytescale(data, cmin=None, cmax=None, high=255, low=0):
    """ Byte scales an array (image).
    Byte scaling means converting the input image to uint8 datatype and scaling
    the range to ``(low, high)`` (default 0-255).
    If the input image already has dtype uint8, no scaling is done.
    This function is only available if Python Imaging Library (PIL) is installed.
    
    data: ndarray
        PIL image data array
    cmin : scalar, optionnal
        Bias scaling of large values. Default is "data.min()"
    cmax : scalar, optional
        Bias scaling of large values. Default is ``data.max()``.
    high : scalar, optional
        Scale max value to `high`.  Default is 255.
    low : scalar, optional
        Scale min value to `low`.  Default is 0.
    Returns
    
    img_array : uint8 ndarray
        The byte-scaled array.
        
    """
    
    
    if data.dtype == uint8:
        return data
    
    if high > 255:
        raise ValueError("high should be less than or equal to 255.")
    
    if low < 0:
        raise ValueError("low should be greater than or equal to 0.")
    
    if high < low:
        raise ValueError("high should be greater or equal to low.")
    
    if cmin is None:
        cmin = data.min()
    if cmax is None:
        cmax = data.max()
    
    cscale = cmax - cmin
    
    if cscale < 0:
        raise ValueError("`cmax` should be larger than `cmin`.")
    elif cscale == 0:
        cscale = 1

    scale = float(high - low) / cscale
    
    bytedata = (data - cmin) * scale + low
    return (bytedata.clip(low, high) + 0.5).astype(uint8)


def imread(name, flatten=False, mode=None):
    """Read an image from a file as an array.
    This function is only available if Python Imaging Library (PIL) is installed.
    Parameters
    ----------
    name : str or file object
        The file name or file object to be read.
    flatten : bool, optional
        If True, flattens the color layers into a single gray-scale layer.
    mode : str, optional
        Mode to convert image to, e.g. ``'RGB'``.  See the Notes for more
        details.
        
        Returns 
        
        -------
        
        imread : ndarray 
            the array obtained by reading the image
            
    """
    im = Image.load(name)
    return fromimage(im, flatten=flatten, mode=mode)

def imsave(name, arr, format=None):
    
    """Save an array as an Image
    name : str or file object 
    arr: ndarray, M*N or M*N*3 or M*N*4
                M*N ==> stand for a gray-scale image        
                M*N*3 ==> stand for a RGB image
                M*N*4 ==> an alpha layer may be included, specified as the last colour band of an 'M*N*4' array.
    format : str
        Image format. if omitted, the format to use is determined from the file name extension. 
        If a file object was used instead of a file name, this parameter should always be used.
    """
    im = toimage(arr, channel_axis=2)
    if format is None:
        im.save(name)
    else:
        im.save(name,format)
    return

def isImageType(t):
    """
    verifie si un objet est bien une image

    
    :param t: objet dont la nature doit etre verifiee
    :returns: True si l'objet est une image
    """
    return hasattr(t, "im")




def fromimage(im, flatten=False, mode=None):
    """
    Return a copy of a PIL image as a numpy array.
    This function is only available if Python Imaging Library (PIL) is installed.
    Parameters
    ----------
    im : PIL image
        Input image.
    flatten : bool
        If true, convert the output to grey-scale.
    mode : str, optional
        Mode to convert image to, e.g. ``'RGB'``.  See the Notes of the
        `imread` docstring for more details.
    Returns
    -------
    fromimage : ndarray
        The different colour bands/channels are stored in the
        third dimension, such that a grey-image is MxN, an
        RGB-image MxNx3 and an RGBA-image MxNx4.
    """
    if not isImageType(im):         ### à corriger
        raise TypeError("Input is not a PIL image.")

    if mode is not None:
        if mode != im.mode: 
            im = im.convert(mode)
    elif im.mode == 'P':
        # Mode 'P' means there is an indexed "palette".  If we leave the mode
        # as 'P', then when we do `a = array(im)` below, `a` will be a 2-D
        # containing the indices into the palette, and not a 3-D array
        # containing the RGB or RGBA values.
        if 'transparency' in im.info:
            im = im.convert('RGBA')
        else:
            im = im.convert('RGB')

    if flatten:
        im = im.convert('F')
    elif im.mode == '1':
        # Workaround for crash in PIL. When im is 1-bit, the call array(im)
        # can cause a seg. fault, or generate garbage. See
        # https://github.com/scipy/scipy/issues/2138 and
        # https://github.com/python-pillow/Pillow/issues/350.
        #
        # This converts im from a 1-bit image to an 8-bit image.
        im = im.convert('L')

    a = array(im)
    return a

_errstr = "Mode is unknown or incompatible with input array shape."

def toimage(arr, high=255, low=0, cmin=None, cmax=None, pal=None,
            mode=None, channel_axis=None):
    """Takes a numpy array and returns a PIL image.
    This function is only available if Python Imaging Library (PIL) is installed.
    The mode of the PIL image depends on the array shape and the `pal` and
    `mode` keywords.
    For 2-D arrays, if `pal` is a valid (N,3) byte-array giving the RGB values
    (from 0 to 255) then ``mode='P'``, otherwise ``mode='L'``, unless mode
    is given as 'F' or 'I' in which case a float and/or integer array is made.
    Notes
    -----
    For 3-D arrays, the `channel_axis` argument tells which dimension of the
    array holds the channel data.
    For 3-D arrays if one of the dimensions is 3, the mode is 'RGB'
    by default or 'YCbCr' if selected.
    The numpy array must be either 2 dimensional or 3 dimensional.
    """
    data = asarray(arr)
    if iscomplexobj(data):
        raise ValueError("Cannot convert a complex-valued array.")
    shape = list(data.shape)
    valid = len(shape) == 2 or ((len(shape) == 3) and
                                ((3 in shape) or (4 in shape)))
    if not valid:
        raise ValueError("'arr' does not have a suitable array shape for "
                         "any mode.")
    if len(shape) == 2:
        shape = (shape[1], shape[0])  # columns show up first
        if mode == 'F':
            data32 = data.astype(numpy.float32)
            image = Image.frombytes(mode, shape, data32.tostring())
            return image
        if mode in [None, 'L', 'P']:
            bytedata = bytescale(data, high=high, low=low,
                                 cmin=cmin, cmax=cmax)
            image = Image.frombytes('L', shape, bytedata.tostring())
            if pal is not None:
                image.putpalette(asarray(pal, dtype=uint8).tostring())
                # Becomes a mode='P' automagically.
            elif mode == 'P':  # default gray-scale
                pal = (arange(0, 256, 1, dtype=uint8)[:, newaxis] *
                       ones((3,), dtype=uint8)[newaxis, :])
                image.putpalette(asarray(pal, dtype=uint8).tostring())
            return image
        if mode == '1':  # high input gives threshold for 1
            bytedata = (data > high)
            image = Image.frombytes('1', shape, bytedata.tostring())
            return image
        if cmin is None:
            cmin = amin(ravel(data))
        if cmax is None:
            cmax = amax(ravel(data))
        data = (data*1.0 - cmin)*(high - low)/(cmax - cmin) + low
        if mode == 'I':
            data32 = data.astype(numpy.uint32)
            image = Image.frombytes(mode, shape, data32.tostring())
        else:
            raise ValueError(_errstr)
        return image

    # if here then 3-d array with a 3 or a 4 in the shape length.
    # Check for 3 in datacube shape --- 'RGB' or 'YCbCr'
    if channel_axis is None:
        if (3 in shape):
            ca = numpy.flatnonzero(asarray(shape) == 3)[0]
        else:
            ca = numpy.flatnonzero(asarray(shape) == 4)
            if len(ca):
                ca = ca[0]
            else:
                raise ValueError("Could not find channel dimension.")
    else:
        ca = channel_axis

    numch = shape[ca]
    if numch not in [3, 4]:
        raise ValueError("Channel axis dimension is not valid.")

    bytedata = bytescale(data, high=high, low=low, cmin=cmin, cmax=cmax)
    if ca == 2:
        strdata = bytedata.tostring()
        shape = (shape[1], shape[0])
    elif ca == 1:
        strdata = transpose(bytedata, (0, 2, 1)).tostring()
        shape = (shape[2], shape[0])
    elif ca == 0:
        strdata = transpose(bytedata, (1, 2, 0)).tostring()
        shape = (shape[2], shape[1])
    if mode is None:
        if numch == 3:
            mode = 'RGB'
        else:
            mode = 'RGBA'

    if mode not in ['RGB', 'RGBA', 'YCbCr', 'CMYK']:
        raise ValueError(_errstr)

    if mode in ['RGB', 'YCbCr']:
        if numch != 3:
            raise ValueError("Invalid array shape for mode.")
    if mode in ['RGBA', 'CMYK']:
        if numch != 4:
            raise ValueError("Invalid array shape for mode.")

    # Here we know data and mode is correct
    image = Image.frombytes(mode, shape, strdata)
    return image

def imrotate(arr, angle, interp='bilinear'):
    """
    Rotate an image counter-clockwise by angle degrees.
    This function is only available if Python Imaging Library (PIL) is installed.
    Parameters
    ----------
    arr : ndarray
        Input array of image to be rotated.
    angle : float
        The angle of rotation.
    interp : str, optional
        Interpolation
        - 'nearest' :  for nearest neighbor
        - 'bilinear' : for bilinear
        - 'lanczos' : for lanczos
        - 'cubic' : for bicubic
        - 'bicubic' : for bicubic
    Returns
    -------
    imrotate : ndarray
        The rotated array of image.
    """
    arr = asarray(arr)
    func = {'nearest': 0, 'lanczos': 1, 'bilinear': 2, 'bicubic': 3, 'cubic': 3}
    im = toimage(arr)
    im = im.rotate(angle, resample=func[interp])
    return fromimage(im)


def imshow(arr):
    """
    Simple showing of an image through an external viewer.
    This function is only available if Python Imaging Library (PIL) is installed.
    Uses the image viewer specified by the environment variable
    SCIPY_PIL_IMAGE_VIEWER, or if that is not defined then `see`,
    to view a temporary file generated from array data.
    Parameters
    ----------
    arr : ndarray
        Array of image data to show.
    Returns
    -------
    None
    Examples
    --------
    >>> a = np.tile(np.arange(255), (255,1))
    >>> from scipy import misc
    >>> misc.imshow(a)
    """
    im = toimage(arr)
    fnum, fname = tempfile.mkstemp('.png')
    try:
        im.save(fname)
    except:
        raise RuntimeError("Error saving temporary image data.")

    import os
    os.close(fnum)

    cmd = os.environ.get('SCIPY_PIL_IMAGE_VIEWER', 'see')
    status = os.system("%s %s" % (cmd, fname))

    os.unlink(fname)
    if status != 0:
        raise RuntimeError('Could not execute image viewer.')


def imresize(arr, size, interp='bilinear', mode=None):
    """
    Resize an image.
    This function is only available if Python Imaging Library (PIL) is installed.
    Parameters
    ----------
    arr : ndarray
        The array of image to be resized.
    size : int, float or tuple
        * int   - Percentage of current size.
        * float - Fraction of current size.
        * tuple - Size of the output image.
    interp : str, optional
        Interpolation to use for re-sizing ('nearest', 'lanczos', 'bilinear', 'bicubic'
        or 'cubic').
    mode : str, optional
        The PIL image mode ('P', 'L', etc.) to convert `arr` before resizing.
    Returns
    -------
    imresize : ndarray
        The resized array of image.
    See Also
    --------
    toimage : Implicitly used to convert `arr` according to `mode`.
    scipy.ndimage.zoom : More generic implementation that does not use PIL.
    """
    im = toimage(arr, mode=mode)
    ts = type(size)
    if issubdtype(ts, int):
        percent = size / 100.0
        size = tuple((array(im.size)*percent).astype(int))
    elif issubdtype(type(size), float):
        size = tuple((array(im.size)*size).astype(int))
    else:
        size = (size[1], size[0])
    func = {'nearest': 0, 'lanczos': 1, 'bilinear': 2, 'bicubic': 3, 'cubic': 3}
    imnew = im.resize(size, resample=func[interp])
    return fromimage(imnew)


def imfilter(arr, ftype):
    """
    Simple filtering of an image.
    This function is only available if Python Imaging Library (PIL) is installed.
    Parameters
    ----------
    arr : ndarray
        The array of Image in which the filter is to be applied.
    ftype : str
        The filter that has to be applied. Legal values are:
        'blur', 'contour', 'detail', 'edge_enhance', 'edge_enhance_more',
        'emboss', 'find_edges', 'smooth', 'smooth_more', 'sharpen'.
    Returns
    -------
    imfilter : ndarray
        The array with filter applied.
    Raises
    ------
    ValueError
        *Unknown filter type.*  If the filter you are trying
        to apply is unsupported.
    """
    _tdict = {'blur': PIL.ImageFilter.BLUR,
              'contour': PIL.ImageFilter.CONTOUR,
              'detail': PIL.ImageFilter.DETAIL,
              'edge_enhance': PIL.ImageFilter.EDGE_ENHANCE,
              'edge_enhance_more': PIL.ImageFilter.EDGE_ENHANCE_MORE,
              'emboss': PIL.ImageFilter.EMBOSS,
              'find_edges': PIL.ImageFilter.FIND_EDGES,
              'smooth': PIL.ImageFilter.SMOOTH,
              'smooth_more': PIL.ImageFilter.SMOOTH_MORE,
              'sharpen': PIL.ImageFilter.SHARPEN
              }

    im = toimage(arr)
    if ftype not in _tdict:
        raise ValueError("Unknown filter type.")
    
    return fromimage(im.filter(_tdict[ftype]))


