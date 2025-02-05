# stdlib
from decimal import Decimal
# libs
import serpy


__all__ = [
    'DecimalField',
]


class DecimalField(serpy.Field):
    _precision: int

    def __init__(self, *args, **kwargs):
        precision = kwargs.pop('precision', 4)
        super(DecimalField, self).__init__(*args, **kwargs)
        self._precision = precision

    def to_value(self, value):
        # Round a decimal to 4 decimal places and cast the result to a string
        rounding_figure = Decimal('1.' + ('0' * self._precision))
        return str(value.quantize(rounding_figure))
