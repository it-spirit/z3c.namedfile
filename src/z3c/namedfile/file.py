# -*- coding: utf-8 -*-

from z3c.namedfile.interfaces import HAVE_BLOBS
from z3c.namedfile.interfaces import INamedFile
from z3c.namedfile.interfaces import INamedImage
from z3c.namedfile.utils import get_contenttype
from zope.app.file.file import File
from zope.app.file.image import Image
from zope.interface import implementer


if HAVE_BLOBS:
    from z3c.blobfile.file import File as BlobFile
    from z3c.blobfile.image import Image as BlobImage
    from z3c.namedfile.interfaces import INamedBlobFile
    from z3c.namedfile.interfaces import INamedBlobImage


@implementer(INamedFile)
class NamedFile(File):
    """A non-BLOB file that stores a filename."""

    def __init__(self, data='', contentType='', filename=None):
        if filename is not None and contentType in \
                ('', 'application/octet-stream'):
            contentType = get_contenttype(filename=filename)
        super(NamedFile, self).__init__(data, contentType)
        self.filename = filename


@implementer(INamedImage)
class NamedImage(Image):
    """An non-BLOB image with a filename."""

    def __init__(self, data='', contentType='', filename=None):
        super(NamedImage, self).__init__(data)
        self.filename = filename

        # Allow override of the image sniffer
        if contentType:
            self.contentType = contentType


if HAVE_BLOBS:

    @implementer(INamedBlobFile)
    class NamedBlobFile(BlobFile):
        """A file stored in a ZODB BLOB, file a filename."""

        def __init__(self, data='', contentType='', filename=None):
            if filename is not None and contentType in \
                    ('', 'application/octet-stream'):
                contentType = get_contenttype(filename=filename)
            super(NamedBlobFile, self).__init__(data, contentType)
            self.filename = filename

    @implementer(INamedBlobImage)
    class NamedBlobImage(BlobImage):
        """An image stored in a ZODB BLOB with a filename."""

        def __init__(self, data='', contentType='', filename=None):
            super(NamedBlobImage, self).__init__(data)
            self.filename = filename

            # Allow override of the image sniffer
            if contentType:
                self.contentType = contentType
