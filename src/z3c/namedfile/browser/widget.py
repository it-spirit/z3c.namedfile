# -*- coding: utf-8 -*-

from z3c.form.browser import file
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IDataManager
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import NOVALUE
from z3c.form.widget import FieldWidget
from z3c.namedfile.browser.interfaces import INamedFileWidget
from z3c.namedfile.browser.interfaces import INamedImageWidget
from z3c.namedfile.browser.scaling import ImageScale
from z3c.namedfile.interfaces import INamed
from z3c.namedfile.interfaces import INamedFileField
from z3c.namedfile.interfaces import INamedImage
from z3c.namedfile.interfaces import INamedImageField
from z3c.namedfile.scale.scale import createScale
from z3c.namedfile.scale.scale import getAvailableSizes
from z3c.namedfile.scale.storage import AnnotationStorage
from z3c.namedfile.utils import safe_basename
from z3c.namedfile.utils import set_headers
from z3c.namedfile.utils import stream_data
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.dublincore.interfaces import IZopeDublinCore
from zope.interface import implementer
from zope.interface import implementsOnly
from zope.location.interfaces import ILocation
from zope.publisher.browser import BrowserView
from zope.publisher.browser import FileUpload
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from zope.security._proxy import _Proxy as Proxy
from zope.security.proxy import removeSecurityProxy
from zope.session.interfaces import ISession
from zope.traversing.browser import absoluteURL

import base64
import datetime
import hashlib
import random
import urllib


try:
    from os import SEEK_END
except ImportError:
    from posixfile import SEEK_END


SESSION_PKG_KEY = 'z3c.namedfile.widget'


def generate_token():
    return base64.b64encode(
        hashlib.sha256(
            str(random.getrandbits(256)) + str(datetime.datetime.now())
        ).digest(),
        random.choice(['rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD'])
    ).rstrip('==')


class NamedFileWidget(file.FileWidget):
    """A widget for a named file object."""
    implementsOnly(INamedFileWidget)

    klass = u'named-file-widget'
    value = None  # don't default to a string
    uploaded_token = None

    def __init__(self, request):
        super(NamedFileWidget, self).__init__(request)
        self.unique_token = generate_token()

    @property
    def allow_nochange(self):
        return not self.ignoreContext and \
            self.field is not None and \
            self.value is not None and \
            self.value != self.field.missing_value

    @property
    def filename(self):
        if self.field is not None and self.value == self.field.missing_value:
            return None
        elif INamed.providedBy(self.value):
            return self.value.filename
        elif isinstance(self.value, FileUpload):
            return safe_basename(self.value.filename)
        else:
            return None

    @property
    def file_size(self):
        if INamed.providedBy(self.value):
            return self.value.getSize() / 1024
        else:
            return 0

    @property
    def filename_encoded(self):
        filename = self.filename
        if filename is None:
            return None
        else:
            if isinstance(filename, unicode):
                filename = filename.encode('utf-8')
            return urllib.quote_plus(filename)

    @property
    def download_url(self):
        if self.field is None:
            return None
        if self.ignoreContext:
            return None
        if self.uploaded_token:
            return None
        try:
            url = absoluteURL(self.form, self.request)
        except TypeError:
            url = self.request.getURL()
        if self.filename_encoded:
            return '{0}/++widget++{1}/@@download/{2}'.format(
                url,
                self.field.__name__,
                self.filename_encoded,
            )
        else:
            return '{0}/++widget++{1}/@@download'.format(
                url,
                self.field.__name__,
            )

    def action(self):
        action = self.request.get('{0}.action'.format(self.name), 'nochange')
        if getattr(self.form, 'successMessage', None) and self.form.status == \
                self.form.successMessage:
            # if form action completed successfully, we want nochange
            action = 'nochange'
        return action

    def extract(self, default=NOVALUE):  # noqa
        action = self.request.get('{0}.action'.format(self.name), None)
        if self.request.get('PATH_INFO', '').endswith(
                'kss_z3cform_inline_validation'):
            action = 'nochange'

        if action == 'remove':
            return None
        elif action == 'nochange':
            session = ISession(self.request)[SESSION_PKG_KEY]
            token = self.uploaded_token
            if token is None:
                token = self.request.get('{0}.token'.format(self.name), None)
            if token in session:
                self.uploaded_token = token
                return session.get(token)
            if self.value is not None:
                return self.value
            if self.ignoreContext:
                return default
            dm = getMultiAdapter((self.context, self.field), IDataManager)
            value = dm.query()

            if isinstance(value, Proxy):
                value = removeSecurityProxy(value)
            return value
        elif action == 'replace':
            # set the action back to 'nochange' so that the button is
            # preselected. Only applicable when form is reloaded with errors
            self.request.form['{0}.action'.format(self.name)] = 'nochange'

        # empty unnamed FileUploads should not count as a value
        value = super(NamedFileWidget, self).extract(default)
        if isinstance(value, FileUpload):
            value.seek(0, SEEK_END)
            empty = value.tell() == 0
            value.seek(0)
            if empty and not value.filename:
                return default
            value.seek(0)
            session = ISession(self.request)[SESSION_PKG_KEY]
            if self.unique_token not in session:
                self.uploaded_token = self.unique_token
                value = IDataConverter(self).toFieldValue(value)
                session[self.unique_token] = value
        elif not value:
            return default
        return value

    def absolute_url(self):
        context = self.context
        if not ILocation.providedBy(context):
            context = self.form.context
        return absoluteURL(context, self.request)


class NamedImageWidget(NamedFileWidget):
    """A widget for a named image object."""
    implementsOnly(INamedImageWidget)

    klass = u'named-image-widget'
    preview_scaling = 'preview'

    @property
    def width(self):
        if INamedImage.providedBy(self.value):
            return self.value.getImageSize()[0]
        else:
            return None

    @property
    def height(self):
        if INamedImage.providedBy(self.value):
            return self.value.getImageSize()[1]
        else:
            return None

    @property
    def preview_url(self):
        if self.field is None:
            return None
        if self.ignoreContext:
            return None
        if self.uploaded_token:
            return None
        try:
            url = absoluteURL(self.form, self.request)
        except TypeError:
            url = self.request.getURL()
        if self.preview_scaling:
            return '{0}/++widget++{1}/@@scaling/{2}'.format(
                url,
                self.field.__name__,
                self.preview_scaling,
            )
        else:
            return '{0}/++widget++{1}/@@scaling'.format(
                url,
                self.field.__name__,
            )

    @property
    def alt(self):
        return self.title

    def modified(self):
        """Provide a callable to return the modification time of content items.

        So stored image scales can be invalidated.
        """
        dc = IZopeDublinCore(self.context)
        return dc.ModificationDate()

    def tag(self, scale='preview', height=None, width=None):
        storage = AnnotationStorage(self.context, self.modified)
        direction = 'thumbnail'

        if height is None and width is None:
            available = getAvailableSizes()
            if scale not in available:
                return None
            width, height = available[scale]
            direction = 'thumbnail'

        info = storage.scale(
            factory=createScale, fieldname=self.field.getName(),
            height=height, width=width, direction=direction,
        )
        if info is not None:
            return ImageScale(self.context, self.request, **info).tag()


@implementer(IPublishTraverse)
class Download(BrowserView):

    def __init__(self, context, request):
        context = removeSecurityProxy(context)
        super(Download, self).__init__(context, request)
        self.filename = None

    def publishTraverse(self, request, name):
        if self.filename is None:
            # ../@@download/filename
            self.filename = name
        else:
            raise NotFound(self, name, request)
        return self

    def __call__(self):
        if self.context.ignoreContext:
            raise NotFound(
                'Cannot get the data file from a widget with no context.'
            )

        context = self.context.context
        field = self.context.field
        dm = getMultiAdapter((context, field,), IDataManager)
        file_ = dm.query()
        if file_ is None:
            raise NotFound(self, self.filename, self.request)
        if not self.filename:
            self.filename = getattr(file_, 'filename', None)
        set_headers(file_, self.request.response, filename=self.filename)
        return stream_data(file_)


@implementer(IPublishTraverse)
class Scaling(BrowserView):

    def __init__(self, context, request):
        context = removeSecurityProxy(context)
        super(Scaling, self).__init__(context, request)
        self.scale = None

    def publishTraverse(self, request, name):
        if self.scale is None:
            # ../@@scaling/scale
            self.scale = name
        else:
            raise NotFound(self, name, request)
        return self

    def __call__(self):
        if self.context.ignoreContext:
            raise NotFound(
                'Cannot get the data image from a widget with no context.'
            )

        context = self.context.context
        field = self.context.field

        if self.scale is not None:
            image_ = self.scale_image(field.getName(), self.scale)
            if image_ is not None:
                image_ = image_.data
        else:
            dm = getMultiAdapter((context, field), IDataManager)
            image_ = dm.query()

        if image_ is None:
            raise NotFound(self, self.scale, self.request)

        set_headers(image_, self.request.response, filename=image_.filename)
        return stream_data(image_)

    def modified(self):
        """Provide a callable to return the modification time of content items.

        So stored image scales can be invalidated.
        """
        unecure_context = removeSecurityProxy(self.context.context)
        # dc = IZopeDublinCore(self.context.context)
        dc = IZopeDublinCore(unecure_context)
        return dc.ModificationDate()

    def scale_image(self, fieldname=None, scale=None, **parameters):
        if scale is not None:
            available = getAvailableSizes()  # self.available_sizes
            if scale not in available:
                return None
            width, height = available[scale]
            parameters.update(width=width, height=height)

        storage = AnnotationStorage(self.context.context, self.modified)
        info = storage.scale(
            factory=createScale, fieldname=fieldname, **parameters
        )

        if info is not None:
            scale_view = ImageScale(self.context.context, self.request, **info)
            return scale_view


@implementer(IFieldWidget)
@adapter(INamedFileField, IFormLayer)
def NamedFileFieldWidget(field, request):
    return FieldWidget(field, NamedFileWidget(request))


@implementer(IFieldWidget)
@adapter(INamedImageField, IFormLayer)
def NamedImageFieldWidget(field, request):
    return FieldWidget(field, NamedImageWidget(request))
