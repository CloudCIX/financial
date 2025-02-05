# libs
import serpy


__all__ = [
    'NominalAccountHistorySerializer',
]


class NominalAccountHistorySerializer(serpy.Serializer):
    """
    address_id:
        description: The id of the Address that the Nominal Ledger transaction was created in
        type: integer
    amount:
        description: The monetary amount that was transferred to/from the Nominal Account
        type: string
        format: decimal
    contra_address_id:
        description: The id of the Address that the Nominal Ledger transaction was made out to
        type: integer
    currency_id:
        description: The id of the currency that is used for the Nominal Account
        type: integer
    name_bill_to:
        description: The name of the Company that the Nominal Ledger transaction was made out to
        type: string
    narrative:
        description: A description of the Nominal Ledger transaction and its items
        type: string
    running_balance:
        description: The outstanding balance in the Nominal Account at the time of the current transaction
        type: string
        format: decimal
    transaction_date:
        description: The date that the Nominal Ledger transaction was created
        type: string
    transaction_type_id:
        description: The id of the Transaction Type for the Nominal Ledger entry
        type: integer
    tsn:
        description: The Transaction Sequence Number of this Nominal Ledger entry
        type: integer
    """
    address_id = serpy.Field()
    amount = serpy.Field()
    contra_address_id = serpy.Field()
    currency_id = serpy.MethodField()
    name_bill_to = serpy.Field()
    narrative = serpy.Field()
    running_balance = serpy.MethodField()
    transaction_date = serpy.Field()
    transaction_type_id = serpy.Field()
    tsn = serpy.Field()

    def __init__(self, *args, **kwargs):
        super(NominalAccountHistorySerializer, self).__init__(*args, **kwargs)
        self.context = kwargs.get('context', dict())

    def get_currency_id(self, obj):
        return self.context.get('currency_id', 'Unavailable')

    def get_running_balance(self, obj):
        try:
            return str(self.context['running_balances'].popleft())
        except (AttributeError, KeyError):  # pragma: no cover
            return '0.0000'
