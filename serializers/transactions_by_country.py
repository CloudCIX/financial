# libs
import serpy
# local


__all__ = [
    'TransactionsByCountrySerializer',
]


class TransactionsByCountrySerializer(serpy.DictSerializer):
    """
    balance:
        description: The balance all sales to a specific country
        type: string
        format: decimal
    country_id:
        description: The id of the Country in which the company sold to.
        type: integer
    excluding_vat:
        description: The sum of all sales excluding VAT processed to a specific country
        type: string
        format: decimal
    vat:
        description: The sum of all VAT processed to a specific country
        type: string
        format: decimal
    """
    balance = serpy.Field()
    country_id = serpy.Field()
    excluding_vat = serpy.Field()
    vat = serpy.Field()
