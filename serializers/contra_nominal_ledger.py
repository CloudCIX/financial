# libs
import serpy
# local
from financial.serializers.nominal_ledger_line import NominalLedgerLineSerializer


__all__ = [
    'ContraNominalLedgerSerializer',
]


class ContraNominalLedgerSerializer(serpy.Serializer):
    """
    address_id:
        description: The id of the Address that created the Nominal Ledger entry
        type: integer
    contact:
        description: The name of the User who created the Nominal Ledger entry
        type: string
    contra_address_id:
        description: |
            The Address id of another Financial User who created a transaction between their own Address and the current
            User's Address
        type: integer
    contra_transaction_type_id:
        description: The id of the Transaction Type that the Contra Nominal Ledger entry uses
        type: integer
    credits:
        $ref: '#/components/schemas/NominalLedgerLine'
    debits:
        $ref: '#/components/schemas/NominalLedgerLine'
    narrative:
        description: A description of the transaction that created the Nominal Ledger entry
        type: string
    total_amount:
        description: The total amount of money involved in the transaction
        type: string
        format: decimal
    transaction_date:
        description: The date that the transaction took place
        type: string
    transaction_type_id:
        description: The id of the Transaction Type that the Nominal Ledger entry uses
        type: integer
    tsn:
        description: |
            The Transaction Sequence Number. Each Transaction Type in an Address has its own Transaction Sequence
            Numbers that begins at one and increments each time a transaction of that type is created.
        type: integer
    unallocated_balance:
        description: The amount left unpaid on a transaction
        type: string
        format: decimal
    """
    address_id = serpy.Field()
    contact = serpy.Field()
    contra_address_id = serpy.Field()
    contra_transaction_type_id = serpy.MethodField()
    credits = serpy.MethodField()
    debits = serpy.MethodField()
    narrative = serpy.Field()
    total_amount = serpy.MethodField()
    transaction_date = serpy.Field()
    transaction_type_id = serpy.Field()
    tsn = serpy.Field()
    unallocated_balance = serpy.Field()

    def __init__(self, *args, **kwargs):
        super(ContraNominalLedgerSerializer, self).__init__(*args, **kwargs)
        # When serializing the `debits` and `credits`, send an empty dict for the `account_names` so that the line
        # serializer won't try to look them up in the db
        self.context = {'account_names': dict()}

    def get_contra_transaction_type_id(self, obj):
        """
        If the transaction type would be for Purchases (Starting at 10000) then the contra would be for Sales (Starting
        at 11000), and vice versa
        :param obj: The object being serialized
        :return: The transaction type id that this object's Contra Transaction would have
        """
        if obj.transaction_type_id >= 11000:
            return obj.transaction_type_id - 1000
        else:
            return obj.transaction_type_id + 1000

    def get_credits(self, obj):
        return NominalLedgerLineSerializer(instance=obj.credits.all(), many=True, context=self.context).data

    def get_debits(self, obj):
        return NominalLedgerLineSerializer(instance=obj.debits.all(), many=True, context=self.context).data

    def get_total_amount(self, obj):
        return str(sum([c.amount for c in obj.credits.all()]))
