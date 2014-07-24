# -*- coding: utf-8 -*-

# python imports
from cStringIO import StringIO
from logging import exception
import logging
import PIL.Image
import PIL.ImageFile

# zope imports
from z3c.namedfile.interfaces import IAvailableSizes
from zope.component import queryUtility
from ZODB.POSException import ConflictError

logger = logging.getLogger('z3c.namedfile')


# Set a larger buffer size. This fixes problems with jpeg decoding.
# See http://mail.python.org/pipermail/image-sig/1999-August/000816.html for
# details.
PIL.ImageFile.MAXBLOCK = 1000000


def scaleImage(
        image, width=None, height=None, direction='down', quality=88,
        result=None):
    """Scale a given image.

    Scale the given image data to another size and return the result as a
    string or optionally write into the file-like `result` object.

    The `image` parameter can either be the raw image data (i.e. a `str`
    instance) or an open file.

    The `quality` parameter can be used to set the quality of the resulting
    image scales.

    The return value is a tuple with the new image, the image format and a
    size-tuple. Optionally a file-like object ca be given as the `result`
    parameter, in which the generated image scale will be stored.

    The `width`, `height` and `direction` parameters will be passed to
    :meth:`scalePILImage`, which performs the actual scaling.
    """
    if isinstance(image, str):
        image = StringIO(image)

    try:
        image = PIL.Image.open(image)
    except IOError, e:
        logger.warning("Error opening image: " + str(e))
        return None

    try:
        image.load()
    except Exception, e:
        logger.warning("Error loading image: " + str(e))
        return None

    # When we create a new image during scaling we loose the format
    # information, so remember it.
    format = image.format
    if not format == 'PNG':
        format = 'JPEG'

    image = scalePILImage(image, width, height, direction)

    if result is None:
        result = StringIO()
        image.save(result, format, quality=quality, optimize=True)
        result = result.getvalue()
    else:
        image.save(result, format, quality=quality, optimize=True)
        result.seek(0)

    return result, format, image.size


def scalePILImage(image, width=None, height=None, direction='down'):
    """Scale a PIL Image to another size.

    The generated image is a JPEG image, unless the original image is a PNG
    image. This is needed to make sure alpha channel information is not lost,
    which JPEG does not support.
    """
    if direction == 'keep':
        direction = 'thumbnail'

    if direction == 'thumbnail' and not (width and height):
        raise ValueError(
            "Thumbnailing requires both width and height to be specified.")
    elif width is None and height is None:
        raise ValueError("Either width or height need to be given.")

    if image.mode == 1:
        # Convert black & white to grayscale.
        image = image.convert("L")
    elif image.mode == 'P':
        # Convert palette based images to 3x8bit+alpha.
        image = image.convert("RGBA")
    elif image.mode == 'CMYK':
        # Convert CMYK to RGB, allowing for web previews of print images.
        image = image.convert("RGB")

    current_size = image.size

#     if (width is not None and width > current_size[0]) and \
#        (height is not None and height > current_size[1]):
#         # We don't scale up
#         return image

    # Determine scale factor needed to get the right height
    if height is None:
        scale_height = None

    else:
        scale_height = (float(height) / float(current_size[1]))

    if width is None:
        scale_width = None
    else:
        scale_width = (float(width) / float(current_size[0]))

    if scale_height == scale_width or direction == 'thumbnail':
        # The original image already has the right aspect ration, so we only
        # need to scale.
        image.thumbnail((width, height), PIL.Image.ANTIALIAS)
    else:
        if direction == 'down':
            if scale_height is None or (
                scale_width is not None and scale_width > scale_height
            ):
                # Width is the smallest dimension (relatively), so scale up to
                # the desired with
                new_width = width
                new_height = int(round(current_size[1] * scale_width))
            else:
                new_height = height
                new_width = int(round(current_size[0] * scale_height))
        else:
            if scale_height is None or (
                scale_width is not None and scale_width < scale_height
            ):
                # Width is the largest dimension (relatively), so scale up to
                # the desired width
                new_width = width
                new_height = int(round(current_size[1] * scale_width))
            else:
                new_height = height
                new_width = int(round(current_size[0] * scale_height))

        image.draft(image.mode, (new_width, new_height))
        image = image.resize((new_width, new_height), PIL.Image.ANTIALIAS)

        if (width is not None and new_width > width) or \
           (height is not None and new_height > height):

            if width is None:
                left = 0
                right = new_width
            else:
                left = int((new_width - width) / 2.0)
                right = left + width

            if height is None:
                height = new_height

            image = image.crop((left, 0, right, height))

    return image


def createScale(context, fieldname, direction='thumbnail', **parameters):
    """Factory for the image scales, see `IImageScaleStorage.scale`."""
    orig_value = getattr(context, fieldname)

    # import ipdb; ipdb.set_trace()
    # if hasattr(orig_value, 'open'):
    #     orig_data = orig_value.open()
    # else:

    orig_data = getattr(orig_value, 'data', orig_value)

    if not orig_data:
        return

    try:
        result = scaleImage(orig_data, direction=direction, **parameters)
    except (ConflictError, KeyboardInterrupt):
        raise
    except Exception:
        exception('Could not scale "%r".', orig_value)
        return

    if result is not None:
        data, format, dimensions = result
        mimetype = 'image/%s' % format.lower()
        value = orig_value.__class__(
            data,
            contentType=mimetype, filename=orig_value.filename,
        )
        value.fieldname = fieldname
        return value, format, dimensions


def getAvailableSizes():
    _sizes = {
        'thumb': (128, 128),
        'mini': (200, 200),
        'preview': (400, 400),
        'large': (768, 768),
    }

    getAvailableSizes = queryUtility(IAvailableSizes)
    if getAvailableSizes is None:
        return _sizes

    sizes = getAvailableSizes()
    if sizes is None:
        return {}

    return sizes
