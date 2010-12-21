# -*- coding: utf-8 -*-

# zope imports
from z3c.form.interfaces import IFileWidget
from zope import schema


class INamedFileWidget(IFileWidget):
    """A widget for a named file field."""

    allow_nochange = schema.Bool(
        title=u"Allow user to keep existing data in lieu of uploading a file?",
    )

    filename = schema.TextLine(
        required=False,
        title=u"Name of the underlaying file.",
    )

    filename_encoded = schema.TextLine(
        required=False,
        title=u"Filename, URL-encoded.",
    )

    file_size = schema.Int(
        default=0,
        required=True,
        title=u"Size in kb.",
    )

    download_url = schema.URI(
        required=False,
        title=u"File download URL.",
    )


class INamedImageWidget(INamedFileWidget):
    """A widget for a named image field."""

    width = schema.Int(
        min=0,
        required=False,
        title=u"Image width.",
    )

    height = schema.Int(
        min=0,
        required=False,
        title=u"Image height.",
    )

    alt = schema.TextLine(
        required=False,
        title=u"Image alternative text.",
    )

    preview_url = schema.URI(
        required=False,
        title=u"Image preview URL.",
    )
