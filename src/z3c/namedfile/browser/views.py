# -*- coding: utf-8 -*-

from datetime import datetime
from z3c.namedfile.utils import get_contenttype
from z3c.namedfile.utils import set_headers
from z3c.namedfile.utils import stream_data
from zope.dublincore.interfaces import IZopeDublinCore
from zope.interface import implementer
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from zope.security.proxy import removeSecurityProxy

import time
import zope.datetime


@implementer(IPublishTraverse)
class Download(BrowserView):
    """Download a file, via ../context/@@download/fieldname/filename

    `fieldname` is the name of an attribute on the context that contains
    the file. `filename` is the filename that the browser will be told to
    give the file. If not given, it will be looked up from the field.

    The attribute under `fieldname` should contain a named (blob) file/image
    instance from this package.
    """

    def __init__(self, context, request):
        super(Download, self).__init__(context, request)
        self.fieldname = None
        self.filename = None

    def publishTraverse(self, request, name):
        if self.fieldname is None:
            # ../@@download/fieldname
            self.fieldname = name
        elif self.filename is None:
            # ../@@download/fieldname/filename
            self.filename = name
        else:
            raise NotFound(self, name, request)
        return self

    def __call__(self):
        # Ensure that we have at least a filedname
        if not self.fieldname:
            raise NotFound(self, '', self.request)

        file = getattr(self.context, self.fieldname, None)
        if file is None:
            raise NotFound(self, self.fieldname, self.request)

        if not self.filename:
            self.filename = getattr(file, 'filename', self.fieldname)

        set_headers(file, self.request.response, filename=self.filename)

        return stream_data(file)


class ScalingView(BrowserView):

    def __call__(self):
        data = removeSecurityProxy(self.context)
        # fieldname = getattr(
        #     data, 'fieldname', getattr(self, 'fieldname', None),
        # )

        try:
            modified = IZopeDublinCore(data.context).modified
        except TypeError:
            modified = None

        if modified is not None and isinstance(modified, datetime):
            header = self.request.getHeader('If-Modified-Since', None)
            if header is not None:
                header = header.split(';')[0]
                try:
                    mod_since = long(zope.datetime.time(header))
                except Exception:
                    mod_since = None

                if mod_since is not None:
                    lmt = long(time.mktime(modified.timetuple()))
                    if lmt <= mod_since:
                        contenttype = get_contenttype(data.data)
                        self.request.response.setHeader(
                            'Content-Type', contenttype,
                        )
                        self.request.response.setStatus(304)
                        return ''

        set_headers(
            data.data, self.request.response,
            filename=data.data.filename, modified=modified,
        )
        return stream_data(data.data)
