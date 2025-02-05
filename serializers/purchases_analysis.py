# libs
import serpy


__all__ = [
    'PurchasesAnalysisSerializer',
]


class PurchasesAnalysisSerializer(serpy.DictSerializer):
    """
    address_id:
        description: The id of the Address
        type: integer
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
    address_id = serpy.Field(attr='contra_address_id')
    total = serpy.StrField()
    total_ex_vat = serpy.StrField()
    vat = serpy.StrField()
