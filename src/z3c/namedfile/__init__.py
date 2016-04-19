# -*- coding: utf-8 -*-
"""File types and fields for images, files and blob files with filenames."""

# python imports
import logging

# local imports
from z3c.namedfile import config
from z3c.namedfile.file import NamedFile, NamedImage
from z3c.namedfile.interfaces import HAVE_BLOBS


if HAVE_BLOBS:
    from z3c.namedfile.file import NamedBlobFile, NamedBlobImage


logger = logging.getLogger(config.PROJECT_NAME)
