# -*- coding: utf-8 -*-

# zope imports
from z3c.form import validator
from zope.schema import ValidationError

# local imports
from z3c.namedfile.interfaces import INamedField


class InvalidState(ValidationError):
    __doc__ = u'No file provided.'


class NamedFileWidgetValidator(validator.SimpleFieldValidator):

    def validate(self, value):
        """See interfaces.IValidator."""

        action = self.request.get('%s.action' % self.widget.name, None)
        if action == 'replace' and value is None:
            raise InvalidState()
        return super(NamedFileWidgetValidator, self).validate(value)


validator.WidgetValidatorDiscriminators(
    NamedFileWidgetValidator,
    field=INamedField,
)
