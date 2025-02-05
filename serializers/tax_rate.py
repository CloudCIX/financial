# libs
import serpy


__all__ = [
    'TaxRateSerializer',
]


class TaxRateSerializer(serpy.Serializer):
    """
    address_id:
        description: The id of the Address that the Tax Rate record belongs to
        type: integer
    created:
        description: Timestamp, in ISO format, of when the Tax Rate record was created.
        type: string
    description:
        description: The kind of Tax Rate being applied, e.g. VAT, Customs Duty, etc.
        type: string
    id:
        description: The id of the Tax Rate record
        type: integer
    percent:
        description: The amount of a transaction that will be claimed as Tax
        type: string
        format: decimal
    updated:
        description: Timestamp, in ISO format, of when the Tax Rate record was last updated.
        type: string
    """
    address_id = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    description = serpy.Field()
    id = serpy.Field()
    percent = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)

    # Backwards Compatibility
    old_address_id = serpy.Field(attr='address_id', label='idAddress')
