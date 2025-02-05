# libs
import serpy
# local
from .allocation_detail import AllocationDetailSerializer

__all__ = [
    'AllocationSerializer',
]


class AllocationSerializer(serpy.Serializer):
    """
    address_id:
        description: The id of the Address that the Allocation belongs to
        type: integer
    allocation_type:
        description: |
            A description that identifies what type of account the Allocation was made for e.g Supplier or Customer
        type: string
    created:
        description: The date the transactions were allocated against each other.
        type: string
    details:
        $ref: '#/components/schemas/AllocationDetail'
    id:
        description: The id of the Allocation record
        type: integer
    uri:
        description: |
            The absolute URL of the Allocation entry that can be used to perform `Read` and `Delete` operations
        type: string
    """
    address_id = serpy.Field(required=False)
    allocation_type = serpy.MethodField()
    created = serpy.Field(attr='created.isoformat', call=True)
    details = AllocationDetailSerializer(many=True, attr='details.iterator', call=True)
    id = serpy.Field()
    uri = serpy.Field(attr='get_absolute_url', call=True)

    # Backwards Compatibility
    old_address_id = serpy.Field(attr='address_id', label='idAddress')

    def get_allocation_type(self, obj):
        return 'Customer' if obj.nominal_account_number == 1300 else 'Supplier'
