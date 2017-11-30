# -*- coding: utf-8 -*-
"""File types and fields for images, files and blob files with filenames."""

from z3c.namedfile import config
from z3c.namedfile.file import NamedFile
from z3c.namedfile.file import NamedImage
from z3c.namedfile.interfaces import HAVE_BLOBS

import logging


if HAVE_BLOBS:
    from z3c.namedfile.file import NamedBlobFile
    from z3c.namedfile.file import NamedBlobImage
    assert(NamedBlobFile)
    assert(NamedBlobImage)

assert(NamedFile)
assert(NamedImage)


logger = logging.getLogger(config.PROJECT_NAME)
