# -*- coding: utf-8 -*-

# local imports
from z3c.namedfile.file import NamedFile, NamedImage
from z3c.namedfile.interfaces import HAVE_BLOBS


if HAVE_BLOBS:
    from z3c.namedfile.file import NamedBlobFile, NamedBlobImage
