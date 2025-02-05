# libs
import serpy


__all__ = [
    'PaymentMethodSerializer',
]


class PaymentMethodSerializer(serpy.Serializer):
    """
    created:
        description: Timestamp, in ISO format, of when the Payment Method record was created.
        type: string
    description:
        description: A description of how a payment can be made, e.g. cheque, cash, bank transfer
        type: string
    id:
        description: The id of the Payment Method record
        type: integer
    member_id:
        description: The id of the Member that this Payment Method record belongs to
        type: integer
    updated:
        description: Timestamp, in ISO format, of when the Payment Method record was last updated.
        type: string
    uri:
        description: The absolute URL of the Payment Method that can be used to perform `Read` and `Update` operations
        type: string

    """
    created = serpy.Field(attr='created.isoformat', call=True)
    description = serpy.Field()
    id = serpy.Field()
    member_id = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)
