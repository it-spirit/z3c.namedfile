# -*- coding: utf-8 -*-

# zope imports
from z3c.form.converter import BaseDataConverter
from zope.component import adapts
from zope.publisher.browser import FileUpload

# local imports
from z3c.namedfile.browser.interfaces import INamedFileWidget
from z3c.namedfile.interfaces import INamed, INamedField
from z3c.namedfile.utils import safe_basename


class NamedDataConverter(BaseDataConverter):
    """Converts from a file-upload to a NamedFile variant."""

    adapts(INamedField, INamedFileWidget)

    def toWidgetValue(self, value):
        return value

    def toFieldValue(self, value):
        if value is None or value == '':
            return self.field.missing_value

        if INamed.providedBy(value):
            return value
        elif isinstance(value, FileUpload):
            headers = value.headers
            filename = safe_basename(value.filename)

            if filename is not None:
                filename = unicode(filename)

            contentType = 'application/octet-stream'
            if headers:
                contentType = headers.get('Content-Type', contentType)

            value.seek(0)
            data = value.read()
            if data or filename:
                return self.field._type(
                    data=data,
                    contentType=contentType,
                    filename=filename,
                )
            else:
                return self.field.missing_value
        else:
            return self.field._type(data=str(value))
