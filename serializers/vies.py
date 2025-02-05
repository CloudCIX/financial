# libs
import serpy


__all__ = [
    'VIESSerializer',
]


class VIESSerializer(serpy.Serializer):
    """
    address_id:
        description: The id of an Address that has done business with the requesting User's Address
        type: integer
    amount:
        description: The total value of transactions for a given combination of Address - Currency - Tax Rate
        type: string
        format: decimal
    """
    address_id = serpy.Field()
    amount = serpy.StrField()
