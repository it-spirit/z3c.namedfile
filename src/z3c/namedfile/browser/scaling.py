# -*- coding: utf-8 -*-

# python imports
from cgi import escape

# zope imports
from ZODB.POSException import ConflictError
from zope.dublincore.interfaces import IZopeDublinCore
from zope.interface import implements
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse, NotFound
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser import absoluteURL
from zope.traversing.interfaces import ITraversable, TraversalError

# local imports
from z3c.namedfile.interfaces import IAvailableSizes
from z3c.namedfile.scale.storage import AnnotationStorage
from z3c.namedfile.scale.scale import scaleImage
from z3c.namedfile.utils import set_headers, stream_data


class ImageScale(BrowserView):

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, context, request, **info):
        self.context = context
        self.request = request
        self.__dict__.update(**info)

        url = absoluteURL(self.context, self.request)
        extension = self.data.contentType.split('/')[-1].lower()

        if 'uid' in info:
            self.__name__ = '%s.%s' % (info['uid'], extension)
            self.url = '%s/@@images/%s' % (url, self.__name__)
        else:
            self.__name__ = info['fieldname']
            self.url = '%s/@@images/%s' % (url, info['fieldname'])

    def absolute_url(self):
        return self.url

    def tag(self, height=None, width=None, alt=None, css_class=None,
        title=None, **kwargs):
        """Create a tag including scale."""
        if height is None:
            height = getattr(self, 'height', self.data.getImageSize()[1])
        if width is None:
            width = getattr(self, 'width', self.data.getImageSize()[0])

        if alt is None:
            alt = u""
        if title is None:
            title = u""

        values = {
            'src': self.url,
            'alt': escape(alt, quote=True),
            'title': escape(title, quote=True),
            'height': height,
            'width': width,
        }

        result = '<img src="%(src)s" alt="%(alt)s" title="%(title)s" ' \
                 'height="%(height)s" width="%(width)s"' % values

        if css_class is not None:
            result = '%s class="%s"' % (result, css_class)

        for key, value in kwargs.items():
            result = '%s %s="%s"' % (result, key, value)

        return '%s />' % result

    def index_html(self):
        """Download the image."""
        fieldname = getattr(self.data, 'fieldname', getattr(self, 'fieldname', None))
        
        set_headers(self.data, self.request.response, filename=self.data.filename)
        return stream_data(self.data)

    def __call__(self):
        # avoid the need to prefix with nocall: in TAL
        return self


class ImageScaling(BrowserView):
    """View used for generating (and storing) image scales."""
    implements(ITraversable, IPublishTraverse)

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
            scale_view = ImageScale(self.context, self.request, data=value,
                fieldname=name)
            return scale_view  # .__of__(self.context)

        if image is not None:
            request.setTraversalStack([])
            return image
        # return self
        raise NotFound(self, name, self.request)

    def traverse(self, name, furtherPath):
        """Used for path traversal, i.e. in zope page templates."""
        value = self.guarded_orig_image(name)
        if not furtherPath:
            image = ImageScale(self.context, self.request, data=value,
                fieldname=name)
        else:
            image = self.scale(name, furtherPath.pop())

        if image is not None:
            return image.tag()

        raise TraversalError(self, name)

    _sizes = {}
    @apply
    def available_sizes():
        def get(self):
            return {
                'thumb': (128, 128),
                'preview': (400, 400),
            }
        def set(self, value):
            self._sizes = value
        return property(get, set)

    def guarded_orig_image(self, fieldname):
        return getattr(self.context, fieldname)

    def create(self, fieldname, direction='thumbnail', **parameters):
        """Factory for the image scales, see `IImageScaleStorage.scale`."""
        orig_value = removeSecurityProxy(getattr(self.context, fieldname))

        if hasattr(orig_value, 'open'):
            orig_data = orig_value.open()
        else:
            orig_data = getattr(orig_value, 'data', orig_value)

        if not orig_data:
            return

        try:
            result = scaleImage(orig_data, direction=direction, **parameters)
        except (ConflictError, KeyboardInterrupt):
            raise
        except Exception:
            exception('Could not scale "%r" or "%r".', orig_value,
                absoluteURL(self.context, self.request))
            return

        if result is not None:
            data, format, dimensions = result
            mimetype = 'image/%s' % format.lower()
            value = orig_value.__class__(data, contentType=mimetype,
                filename=orig_value.filename)
            value.fieldname = fieldname
            return value, format, dimensions

    def modified(self):
        """Provide a callable to return the modification time of content items.

        So stored image scales can be invalidated.
        """
        dc = IZopeDublinCore(self.context)
        return dc.ModificationDate()

    def scale(self, fieldname=None, scale=None, **parameters):
        if scale is not None:
            available = self.available_sizes
            if not scale in available:
                return None
            width, height = available[scale]
            parameters.update(width=width, height=height)

        storage = AnnotationStorage(self.context, self.modified)
        info = storage.scale(factory=self.create, fieldname=fieldname,
            **parameters)

        if info is not None:
            scale_view = ImageScale(self.context, self.request, **info)
            return scale_view  # .__of__(self.context)
