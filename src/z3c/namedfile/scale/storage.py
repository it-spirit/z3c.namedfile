# -*- coding: utf-8 -*-
"""Image scaling storage."""

from datetime import timedelta
from persistent.dict import PersistentDict
from UserDict import DictMixin
from uuid import uuid4
from z3c.namedfile import logger
from zope.annotation import IAnnotations
from zope.dublincore.interfaces import IZopeDublinCore
from zope.interface import implementer
from zope.interface import Interface
from zope.security.proxy import Proxy
from zope.security.proxy import removeSecurityProxy


# Keep old scales around for this amount of milliseconds.
# This is one day:
KEEP_SCALE_DAYS = 1


class IImageScaleStorage(Interface):
    """Image Scale Storage Adapter.

    This is an adapter for image content which can store, retrieve and generate
    image scale data. It provides a dictionary interface to existing image
    scales using the scale id as key. To find or create a scale based on its
    scaling parameters use the :meth:`scale` method.
    """

    def __init__(context, modified=None):
        """Adapter initialization.

        Adapt the given context item and optionally provide a callable to
        return a representation of the last modification date, which can be
        used to invalidate stored scale data on update.
        """

    def scale(factory=None, **parameters):
        """Find or create scalings.

        Find image scale data for the given parameters or create it if a
        factory was provided. The parameters will be passed back to the factory
        method, which is expected to return a tuple containing a representation
        of the actual image scale data (i.e. a string or file-like object) as
        well as the image's format and dimensions. For convenience, this
        happens to match the return value of `scaleImage`, but makes it
        possible to use different storages, i.e. ZODB blobs.
        """

    def __getitem__(uid):
        """Find image scale data based on its uid."""


@implementer(IImageScaleStorage)
class AnnotationStorage(DictMixin):
    """Abstract image storage mixin.

    An abstract storage for image scale data using annotations and implementing
    :class:`IImageScaleStorage`. Image data is stored as an annotation on the
    object container, i.e. the image. This is needed since not all images are
    themselves annotatable.
    """

    def __init__(self, context, modified=None):
        self.context = context
        self.modified = modified

    def __repr__(self):
        name = self.__class__.__name__
        return '<{0} context={1}>'.format(name, self.context)

    __str__ = __repr__

    @property
    def storage(self):
        return IAnnotations(removeSecurityProxy(self.context)).setdefault(
            'z3c.namedfile.scale', PersistentDict())

    def hash(self, **parameters):
        return tuple(sorted(parameters.items()))

    def scale(self, factory=None, **parameters):
        key = self.hash(**parameters)
        storage = self.storage
        info = storage.get(key)
        try:
            modified = self.modified and self.modified()
        except TypeError:
            modified = self.modified and self.context.modified()

        if info is not None and modified > info['modified']:
            del storage[key]
            # invalidate when the image was updated
            info = None

        if info is None and factory:
            result = factory(removeSecurityProxy(self.context), **parameters)
            if result is not None:
                # storage will be modified:
                # good time to also cleanup
                self._cleanup()
                data, format, dimensions = result
                width, height = dimensions
                uid = str(uuid4())
                info = dict(
                    uid=uid, data=data, width=width, height=height,
                    mimetype='image/{0}'.format(format.lower()), key=key,
                    modified=modified,
                )
                storage[key] = storage[uid] = info
        return info

    def __getitem__(self, uid):
        return self.storage[uid]

    def __setitem__(self, id, scale):
        raise RuntimeError('New scales have to be created via scale().')

    def __delitem__(self, uid):
        storage = self.storage
        info = storage[uid]
        del storage[info['key']]
        del storage[uid]

    def __iter__(self):
        return iter(self.storage)

    def keys(self):
        return self.storage.keys()

    def has_key(self, uid):
        return uid in self.storage

    __contains__ = has_key

    def _cleanup(self, force=False):
        storage = self.storage
        count = len(self.keys())
        if count == 0:
            return

        logger.debug('Object: {0}, Scales: {1}'.format(
            self.context.__name__,
            count,
        ))
        modified_time = self.modified_time
        if modified_time is None:
            if not force:
                return
        else:
            keep_time = modified_time - timedelta(days=KEEP_SCALE_DAYS)
            keep_time_iso = keep_time.isoformat()
        for key, value in storage.items():
            # clear cache from scales older than one day
            if (modified_time and value['modified'] < keep_time_iso) or force:
                logger.debug('Removed scale from {0} with key {1}'.format(
                    self.context,
                    key,
                ))
                del storage[key]

    @property
    def modified_time(self):
        context = self.context
        if isinstance(context, Proxy):
            context = removeSecurityProxy(context)
        try:
            dc = IZopeDublinCore(context)
        except Exception:
            return None
        else:
            return dc.modified
