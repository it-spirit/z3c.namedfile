# -*- coding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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
""""""

from z3c.namedfile.browser.scaling import ImageScale
from z3c.namedfile.scale.scale import createScale, getAvailableSizes
from z3c.namedfile.scale.storage import AnnotationStorage
from zope.component.interfaces import ComponentLookupError
from zope.dublincore.interfaces import IZopeDublinCore

def modified(context):
    """Provide a callable to return the modification time of content items.

    So stored image scales can be invalidated.
    """
    dc = IZopeDublinCore(context)
    return dc.ModificationDate()


def scale(context, request, fieldname, scale='preview', height=None,
          width=None, fallback=(400,400)):
    storage = AnnotationStorage(context, modified(context))
    direction = 'thumbnail'

    if height is None and width is None:
        available = getAvailableSizes()
        if not scale in available:
            width, height = fallback
        else:
            width, height = available[scale]
        direction = 'thumbnail'

    try:
        info = storage.scale(factory=createScale, fieldname=fieldname,
                             height=height, width=width, direction=direction)
    except ComponentLookupError:
        info = None
    if info is not None:
        return ImageScale(context, request, **info)

def tag(context, request, fieldname, scaling):
    return scale(context, request, fieldname, scale=scaling).tag(alt=context.title, title=context.title)
