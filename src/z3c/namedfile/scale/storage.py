# -*- coding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Image scaling storage.

"""

# python imports
from UserDict import DictMixin
from uuid import uuid4

# zope imports
from persistent.dict import PersistentDict
from zope.annotation import IAnnotations
from zope.interface import implements, Interface
from zope.security.proxy import removeSecurityProxy


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


class AnnotationStorage(DictMixin):
    """Abstract image storage mixin.

    An abstract storage for image scale data using annotations and implementing
    :class:`IImageScaleStorage`. Image data is stored as an annotation on the
    object container, i.e. the image. This is needed since not all images are
    themselves annotatable.
    """
    implements(IImageScaleStorage)

    def __init__(self, context, modified=None):
        self.context = context
        self.modified = modified

    def __repr__(self):
        name = self.__class__.__name__
        return '<%s context=%r>' % (name, self.context)

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
        modified = self.modified and self.modified()

        if info is not None and modified > info['modified']:
            # invalidate when the image was updated
            info = None

        if info is None and factory:
            result = factory(**parameters)
            if result is not None:
                data, format, dimensions = result
                width, height = dimensions
                uid = str(uuid4())
                info = dict(uid=uid, data=data, width=width, height=height,
                    mimetype='image/%s' % format.lower(), key=key,
                    modified=modified)
                storage[key] = storage[uid] = info
        return info

    def __getitem__(self, uid):
        return self.storage[uid]

    def __setitem__(self, id, scale):
        raise RuntimeError("New scales have to be created via scale().")

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
        return self.storage.has_key(uid)

    __contains__ = has_key
