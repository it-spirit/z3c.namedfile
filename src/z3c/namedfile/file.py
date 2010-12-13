# -*- coding: utf-8 -*-

# zope imports
from zope.app.file.file import File
from zope.app.file.image import Image
from zope.interface import implements

# local imports
from z3c.namedfile.interfaces import HAVE_BLOBS, INamedFile, INamedImage
from z3c.namedfile.utils import get_contenttype

if HAVE_BLOBS:
    from z3c.blobfile.file import File as BlobFile
    from z3c.blobfile.image import Image as BlobImage
    from plone.namedfile.interfaces import INamedBlobFile, INamedBlobImage


class NamedFile(File):
    """A non-BLOB file that stores a filename."""
    implements(INamedFile)

    def __init__(self, data='', contentType='', filename=None):
        if filename is not None and contentType in \
            ('', 'application/octet-stream'):
            contentType = get_contenttype(filename=filename)
        super(NamedFile, self).__init__(data, contentType)
        self.filename = filename


class NamedImage(Image):
    """An non-BLOB image with a filename."""
    implements(INamedImage)

    def __init__(self, data='', contentType='', filename=None):
        super(NamedImage, self).__init__(data)
        self.filename = filename

        # Allow override of the image sniffer
        if contentType:
            self.contentType = contentType
