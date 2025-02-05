# stdlib
from itertools import chain
# libs
import serpy
# local
from financial.models.address_nominal_account import AddressNominalAccount
from financial.serializers.email_log import EmailLogSerializer
from financial.serializers.nominal_ledger_line import NominalLedgerLineSerializer


__all__ = [
    'YearEndSerializer',
]


class YearEndSerializer(serpy.Serializer):
    """
    address_id:
        description: The id of the Address that created the Year End transaction
        type: integer
    contact:
        description: The name of the User who created the Nominal Ledger entry
        type: string
    credits:
        $ref: '#/components/schemas/NominalLedgerLine'
    debits:
        $ref: '#/components/schemas/NominalLedgerLine'
    email_log:
        $ref: '#/components/schemas/EmailLog'
    narrative:
        description: A description of the transaction that created the Nominal Ledger entry
        type: string
    period_end_balance:
        description: The sum of all transactions from the last Period End
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
    uri:
        description: |
            The absolute URL of the Nominal Ledger entry that can be used to perform `Read` and `Update` operations
        type: string
    """
    address_id = serpy.Field()
    contact = serpy.Field()
    credits = serpy.MethodField()
    debits = serpy.MethodField()
    email_log = EmailLogSerializer(many=True, attr='email_log.all', call=True)
    narrative = serpy.Field()
    period_end_balance = serpy.StrField()
    transaction_date = serpy.Field(attr='transaction_date.isoformat', call=True)
    transaction_type_id = serpy.Field()
    tsn = serpy.Field()
    uri = serpy.Field(attr='get_absolute_url', call=True)

    def __init__(self, *args, **kwargs):
        super(YearEndSerializer, self).__init__(*args, **kwargs)
        self.context = kwargs.get('context', dict())

        if self.instance is not None:
            self.context['account_names'] = self.get_account_names()

    def get_account_names(self):
        # Gather the account numbers from all the `debit` and `credit` records to be serialized so we can fetch all the
        # account names in one query
        if self.many:
            # A queryset is being serialized
            entries = self.instance
        else:
            # One object is being serialized
            entries = [self.instance]

        # Get all the unique Nominal Account Numbers
        account_numbers = set()
        for entry in entries:
            for line in chain(entry.debits.all(), entry.credits.all()):
                account_numbers.add(line.nominal_account_number)

        account_names = dict()
        if len(account_numbers) > 0:
            # Get Address Nominal Account descriptions
            accounts = AddressNominalAccount.objects.filter(
                address_id=entries[0].address_id,
                global_nominal_account__nominal_account_number__in=account_numbers,
            ).values('global_nominal_account__nominal_account_number', 'description')

            # Iterate through the accounts and make a dict of the values
            for a in accounts.iterator():
                account_names[a['global_nominal_account__nominal_account_number']] = a['description']

        return account_names

    def get_credits(self, obj):
        return NominalLedgerLineSerializer(instance=obj.credits.all(), many=True, context=self.context).data

    def get_debits(self, obj):
        return NominalLedgerLineSerializer(instance=obj.debits.all(), many=True, context=self.context).data
