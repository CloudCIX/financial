# libs
import serpy
# local
from financial.serializers.global_nominal_account import GlobalNominalAccountSerializer


__all__ = [
    'StatementSerializer',
]


class StatementSerializer(serpy.Serializer):
    """
    balance:
        description: The amount outstanding in the account
        type: string
        format: decimal
    nominal_account:
        $ref: '#/components/schemas/GlobalNominalAccount'
    total_credits:
        description: The sum of all credits in the account
        type: string
        format: decimal
    total_debits:
        description: The sum of all debits in the account
        type: string
        format: decimal
    """
    balance = serpy.StrField()
    nominal_account = GlobalNominalAccountSerializer()
    total_credits = serpy.StrField()
    total_debits = serpy.StrField()
