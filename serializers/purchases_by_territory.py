# libs
import serpy


__all__ = [
    'PurchasesByTerritorySerializer',
]


class PurchasesByTerritorySerializer(serpy.DictSerializer):
    """
    address_id:
        description: The id of the Address
        type: integer
    full_address:
        description: The full geographic address of the Address
        type: string
    name:
        description: The name of an Address
        type: string
    total:
        description: The total value of goods purchased from an Address
        type: string
        format: decimal
    total_ex_vat:
        description: The total value of goods purchased from an Address excluding VAT
        type: string
        format: decimal
    vat:
        description: The total VAT on goods purchased from an Address
        type: string
        format: decimal
    """
    address_id = serpy.Field(attr='id')
    full_address = serpy.Field()
    name = serpy.Field()
    total = serpy.StrField()
    total_ex_vat = serpy.StrField()
    vat = serpy.StrField()
