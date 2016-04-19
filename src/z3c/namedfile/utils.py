# -*- coding: utf-8 -*-

# python imports
import datetime
import mimetypes
import os.path
import time
import urllib

import zope.datetime

# local imports
from z3c.namedfile.interfaces import INamedFile


def safe_basename(filename):
    """Get the basename of the given filename.

    Regardless of which platform (Windows or Unix) it originated from.
    """
    return filename[max(filename.rfind('/'),
                        filename.rfind('\\'),
                        filename.rfind(':'),
                        ) + 1:]


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


def set_headers(file, response, filename=None, modified=None):
    """Set response headers for the given file.

    If filename is given, set the Content-Disposition to attachment.
    """
    contenttype = get_contenttype(file)

    response.setHeader('Content-Type', contenttype)
    response.setHeader('Content-Length', file.getSize())
    response.setHeader('Cache-Control', 'public,max-age=86400')
    expires = (datetime.datetime.utcnow() + datetime.timedelta(days=1))
    expires = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
    response.setHeader('Expires', expires)

    if modified is not None and isinstance(modified, datetime.datetime):
        # modified = modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
        modified = zope.datetime.rfc1123_date(
            long(time.mktime(modified.timetuple()))
        )
        response.setHeader('Last-Modified', modified)

    if INamedFile.providedBy(file) and filename is not None:
        if not isinstance(filename, unicode):
            filename = unicode(filename, 'utf-8', errors='ignore')
        filename = urllib.quote(filename.encode('utf8'))
        response.setHeader(
            'Content-Disposition',
            'attachment; filename*=UTF-8\'\'{0}'.format(filename),
        )


def stream_data(file):
    """Return the given file as a stream if possible."""
    return file.data
