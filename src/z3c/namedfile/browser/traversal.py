# -*- coding: utf-8 -*-

# zope imports
from zope.interface import implementer
from zope.security.proxy import removeSecurityProxy
from zope.traversing.interfaces import ITraversable


@implementer(ITraversable)
class WidgetTraversable(object):
    """Traverser from a z3c.form to its widgets.

    /context/@@form/++widget++fieldname is the widget belonging to the form
    field 'fieldname'.
    """

    def __init__(self, context, request):
        self.context = removeSecurityProxy(context)
        self.request = request

    def traverse(self, name, remaining):
        form = self.context
        form.update()
        if getattr(form, 'groups', None) is not None:
            widget = self.find_widget(form, name)
        else:
            widget = form.widgets[name]
        return widget

    def find_widget(self, form, name):
        for group in form.groups:
            widget = group.widgets.get(name)
            if widget:
                return widget
