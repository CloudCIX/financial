# libs
import serpy
# local
from .nominal_ledger import NominalLedgerSerializer


__all__ = [
    'AllocationDetailSerializer',
]


class AllocationDetailSerializer(serpy.Serializer):
    """
    credit_amount:
        description: The amount of the Allocation that is credited
        type: integer
    debit_amount:
        description: The amount of the Allocation that is debited
        type: integer
    id:
        description: The id of the Allocation Detailrecord
        type: integer
    nominal_ledger:
        $ref: '#/components/schemas/NominalLedger'
    """

    credit_amount = serpy.StrField()
    debit_amount = serpy.StrField()
    id = serpy.Field()
    nominal_ledger = NominalLedgerSerializer()

    # Backwards Compatibility
    old_credit_amount = serpy.Field(attr='credit_amount', label='totalCredits')
    old_debit_amount = serpy.Field(attr='debit_amount', label='totalDebits')
    old_nominal_ledger = NominalLedgerSerializer(attr='nominal_ledger', label='journal')
