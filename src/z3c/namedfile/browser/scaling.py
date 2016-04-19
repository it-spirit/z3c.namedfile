# -*- coding: utf-8 -*-
"""Image scaling."""

# python imports
from cgi import escape

# zope imports
from zope.dublincore.interfaces import IZopeDublinCore
from zope.interface import implementer
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import (
    IPublishTraverse,
    NotFound,
)
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser import absoluteURL
from zope.traversing.interfaces import ITraversable

# local imports
from z3c.namedfile.scale.storage import AnnotationStorage
from z3c.namedfile.scale.scale import (
    createScale,
    getAvailableSizes,
)
from z3c.namedfile.utils import (
    set_headers,
    stream_data,
)


class ImageScale(BrowserView):

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, context, request, **info):
        self.context = context
        self.request = request
        self.__dict__.update(**info)

        url = absoluteURL(self.context, self.request)
        extension = self.data.contentType.split('/')[-1].lower()

        if 'uid' in info:
            self.__name__ = '{0}.{1}'.format(info['uid'], extension)
            self.url = '{0}/@@scaling/{1}'.format(url, self.__name__)
        else:
            self.__name__ = info['fieldname']
            self.url = '{0}/@@scaling/{1}'.format(url, info['fieldname'])

    def absolute_url(self):
        return self.url

    def tag(
            self, height=None, width=None, alt=None, css_class=None,
            title=None, **kwargs):
        """Create a tag including scale."""
        if height is None:
            height = getattr(self, 'height', self.data.getImageSize()[1])
        if width is None:
            width = getattr(self, 'width', self.data.getImageSize()[0])

        if alt is None:
            alt = u''
        if title is None:
            title = u''

        values = {
            'src': self.url,
            'alt': escape(alt, quote=True),
            'title': escape(title, quote=True),
            'height': height,
            'width': width,
        }

        result = '<img src="{src}" alt="{alt}" title="{title}" ' \
                 'height="{height}" width="{width}"'.format(**values)

        if css_class is not None:
            result = '{0} class="{1}"'.format(result, css_class)

        for key, value in kwargs.items():
            result = '{0} {1}="{2}"'.format(result, key, value)

        return '{0} />'.format(result)

    def index_html(self):
        """Download the image."""
        set_headers(
            self.data, self.request.response,
            filename=self.data.filename,
        )
        return stream_data(self.data)

    def __call__(self):
        # avoid the need to prefix with nocall: in TAL
        return self


@implementer(ITraversable, IPublishTraverse)
class ImageScaling(BrowserView):
    """View used for generating (and storing) image scales."""

    def __init__(self, context, request):
        self.context = removeSecurityProxy(context)
        self.request = request

    def publishTraverse(self, request, name):
        """Used for traversal via publisher, i.e. when using as a url."""
        stack = request.getTraversalStack()
        image = None
        if stack:
            # field and scale name were given...
            scale = stack.pop()
            image = self.scale(name, scale)
        elif '.' in name:
            # we got a uid...
            uid, ext = name.rsplit('.', 1)
            storage = AnnotationStorage(self.context)
            info = storage.get(uid)
            if info is not None:
                scale_view = ImageScale(self.context, self.request, **info)
                return scale_view  # .__of__(self.context)
        else:
            # otherwise `name` must refer to a field...
            value = getattr(self.context, name)
            scale_view = ImageScale(
                self.context, self.request,
                data=value, fieldname=name,
            )
            return scale_view  # .__of__(self.context)

        if image is not None:
            request.setTraversalStack([])
            return image
        # return self
        raise NotFound(self, name, self.request)

    def modified(self):
        """Provide a callable to return the modification time of content items.

        So stored image scales can be invalidated.
        """
        dc = IZopeDublinCore(self.context)
        return dc.ModificationDate()

    def scale(self, fieldname=None, scale=None, **parameters):
        if scale is not None:
            available = getAvailableSizes()
            if scale not in available:
                return None
            width, height = available[scale]
            parameters.update(width=width, height=height)

        storage = AnnotationStorage(self.context, self.modified)
        info = storage.scale(
            factory=createScale, fieldname=fieldname, **parameters
        )

        if info is not None:
            scale_view = ImageScale(self.context, self.request, **info)
            return scale_view  # .__of__(self.context)
