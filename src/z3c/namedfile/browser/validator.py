# -*- coding: utf-8 -*-

from z3c.form import validator
from z3c.namedfile.interfaces import INamedField
from zope.schema import ValidationError


class InvalidState(ValidationError):
    __doc__ = u'No file provided.'


class NamedFileWidgetValidator(validator.SimpleFieldValidator):

    def validate(self, value):
        """See interfaces.IValidator."""

        action = self.request.get('{0}.action'.format(self.widget.name), None)
        if action == 'replace' and value is None:
            raise InvalidState()
        return super(NamedFileWidgetValidator, self).validate(value)


validator.WidgetValidatorDiscriminators(
    NamedFileWidgetValidator,
    field=INamedField,
)
