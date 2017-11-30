# -*- coding: utf-8 -*-

from z3c.namedfile.file import NamedFile as FileValueType
from z3c.namedfile.file import NamedImage as ImageValueType
from z3c.namedfile.interfaces import HAVE_BLOBS
from z3c.namedfile.interfaces import INamedFile
from z3c.namedfile.interfaces import INamedFileField
from z3c.namedfile.interfaces import INamedImage
from z3c.namedfile.interfaces import INamedImageField
from zope.interface import implementer
from zope.schema import Object


if HAVE_BLOBS:
    from z3c.namedfile.file import NamedBlobFile as BlobFileValueType
    from z3c.namedfile.file import NamedBlobImage as BlobImageValueType
    from z3c.namedfile.interfaces import INamedBlobFile
    from z3c.namedfile.interfaces import INamedBlobFileField
    from z3c.namedfile.interfaces import INamedBlobImage
    from z3c.namedfile.interfaces import INamedBlobImageField


@implementer(INamedFileField)
class NamedFile(Object):
    """A NamedFile field."""

    _type = FileValueType
    schema = INamedFile

    def __init__(self, **kw):
        if 'schema' in kw:
            self.schema = kw.pop('schema')
        super(NamedFile, self).__init__(schema=self.schema, **kw)


@implementer(INamedImageField)
class NamedImage(Object):
    """A NamedImage field."""

    _type = ImageValueType
    schema = INamedImage

    def __init__(self, **kw):
        if 'schema' in kw:
            self.schema = kw.pop('schema')
        super(NamedImage, self).__init__(schema=self.schema, **kw)


if HAVE_BLOBS:

    @implementer(INamedBlobFileField)
    class NamedBlobFile(Object):
        """A NamedBlobFile field."""

        _type = BlobFileValueType
        schema = INamedBlobFile

        def __init__(self, **kw):
            if 'schema' in kw:
                self.schema = kw.pop('schema')
            super(NamedBlobFile, self).__init__(schema=self.schema, **kw)

    @implementer(INamedBlobImageField)
    class NamedBlobImage(Object):
        """A NamedBlobImage field."""

        _type = BlobImageValueType
        schema = INamedBlobImage

        def __init__(self, **kw):
            if 'schema' in kw:
                self.schema = kw.pop('schema')
            super(NamedBlobImage, self).__init__(schema=self.schema, **kw)
