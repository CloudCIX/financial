"""
Dummy serializers to generate VAT3 schema
"""
# libs
import serpy

__all__ = [
    'VAT3Serializer',
]


class VAT3Serializer(serpy.Serializer):
    """
    eu_purchases:
        description: The total value of goods purchased from countries in the EU
        type: string
        format: decimal
    eu_sales:
        description: The total value of goods sold to countries in the EU
        type: string
        format: decimal
    net_payable:
        description: The total VAT on sales less the total VAT on purchases
        type: string
        format: decimal
    vat_on_purchases:
        description: The total VAT amount on purchase transactions
        type: string
        format: decimal
    vat_on_sales:
        description: The total VAT amount on sale transactions
        type: string
        format: decimal
    """
    eu_purchases = serpy.Field()
    eu_sales = serpy.Field()
    net_payable = serpy.Field()
    vat_on_purchases = serpy.Field()
    vat_on_sales = serpy.Field()
