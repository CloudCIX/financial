# libs
import serpy

__all__ = [
    'StatementLogSerializer',
]


class StatementLogSerializer(serpy.Serializer):
    """
    address_id:
        description: The id of the Address that created the Statement
        type: integer
    comment:
        description: Description of why the Statement was sent
        type: string
    contra_address_id:
        description: The id of the Address that the Statement was issued to
        type: integer
    created:
        description: Timestamp, in ISO format, of when the Statement Log record was last updated.
        type: string
    status:
        description: Descriptor of whether the Statement was sent successfully
        type: string
    """
    address_id = serpy.IntField()
    comment = serpy.StrField()
    contra_address_id = serpy.IntField()
    created = serpy.Field(attr='created.isoformat', call=True)
    status = serpy.StrField()
