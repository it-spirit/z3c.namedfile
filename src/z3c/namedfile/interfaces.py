# -*- coding: utf-8 -*-

from zope import schema
from zope.app.file.interfaces import IFile
from zope.app.file.interfaces import IImage
from zope.interface import Interface
from zope.schema.interfaces import IObject

import pkg_resources


try:
    pkg_resources.get_distribution('z3c.blobfile')
except pkg_resources.DistributionNotFound:
    HAVE_BLOBS = False
else:
    HAVE_BLOBS = True
    from z3c.blobfile.interfaces import IBlobFile, IBlobImage


class IImageScaleTraversable(Interface):
    """Marker for items that should provide access to image scales for named
    image fields via the @@images view."""


class IAvailableSizes(Interface):
    """A callable returning a dictionary of scale name => (width, height)."""


class INamed(Interface):
    """An item with a filename."""

    filename = schema.TextLine(
        default=None,
        required=False,
        title=u'Filename',
    )


class INamedFile(INamed, IFile):
    """A non-BLOB file with a filename."""


class INamedImage(INamed, IImage):
    """A non-BLOB image with a filename."""


class INamedField(IObject):
    """Base field type."""


class INamedFileField(INamedField):
    """Field for storing INamedFile objects."""


class INamedImageField(INamedField):
    """Field for storing INamedImage objects."""


if HAVE_BLOBS:

    class IBlobby(Interface):
        """Marker interface for objects that support blobs."""

    class INamedBlobFile(INamedFile, IBlobby, IBlobFile):
        """A BLOB file with a filename."""

    class INamedBlobImage(INamedImage, IBlobby, IBlobImage):
        """A BLOB image with a filename."""

    class INamedBlobFileField(INamedFileField):
        """Field for storing INamedBlobFile objects."""

    class INamedBlobImageField(INamedImageField):
        """Field for storing INamedBlobImage objects."""
