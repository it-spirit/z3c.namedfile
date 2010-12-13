# -*- coding: utf-8 -*-

# python imports
import mimetypes
import os.path

# local imports
from z3c.namedfile.interfaces import HAVE_BLOBS

if HAVE_BLOBS:
    from z3c.namedfile.interfaces import IBlobby


def get_contenttype(file=None, filename=None,
                    default='application/octet-stream'):
    """Get the MIME content type of the given file and/or filename."""

    file_type = getattr(file, 'contentType', None)
    if file_type is not None:
        return file_type

    filename = getattr(file, 'filename', filename)
    if filename:
        extension = os.path.splitext(filename)[1].lower()
        return mimetypes.types_map.get(extension, 'application/octet-stream')

    return default
