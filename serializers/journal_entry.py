# stdlib
from itertools import chain
# libs
import serpy
# local
from financial.models.address_nominal_account import AddressNominalAccount
from financial.serializers.email_log import EmailLogSerializer
from financial.serializers.nominal_ledger_line import NominalLedgerLineSerializer


__all__ = [
    'JournalEntrySerializer',
]


class JournalEntrySerializer(serpy.Serializer):
    """
    address_id:
        description: The id of the Address that created the Nominal Ledger entry
        type: integer
    address1_bill_to:
        description: The first line of the address to bill for the transaction
        type: string
    address2_bill_to:
        description: The second line of the address to bill for the transaction
        type: string
    address3_bill_to:
        description: The third line of the address to bill for the transaction
        type: string
    city_bill_to:
        description: The city in which the company to bill for the transaction line is located
        type: string
    contact:
        description: The name of the User who created the Nominal Ledger entry
        type: string
    country_id_bill_to:
        description: The id of the Country in which the company to bill for the transaction is located
        type: integer
    created:
        description: The date that the Nominal Ledger entry was created
        type: string
    credits:
        $ref: '#/components/schemas/NominalLedgerLine'
    debits:
        $ref: '#/components/schemas/NominalLedgerLine'
    email_log:
        $ref: '#/components/schemas/EmailLog'
    id:
        description: The id of the Nominal Ledger record
        type: integer
    name_bill_to:
        description: The name of the company that the transaction will be billed to
        type: string
    narrative:
        description: A description of the transaction that created the Nominal Ledger entry
        type: string
    postcode_bill_to:
        description: The postcode of the company that the transaction will be billed to
        type: string
    report_template_id:
        description: The id of the Report Template to use when printing this Nominal Ledger entry
        type: integer
    subdivision_id_bill_to:
        description: The id of the Subdivision in which the company to bill for the transaction is located
        type: integer
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
        format: decimal
    updated:
        description: The date that the Nominal Ledger entry was last updated
        type: string
    uri:
        description: |
            The absolute URL of the Nominal Ledger entry that can be used to perform `Read` and `Update` operations
        type: string
    """
    address_id = serpy.Field()
    address1_bill_to = serpy.Field()
    address2_bill_to = serpy.Field()
    address3_bill_to = serpy.Field()
    city_bill_to = serpy.Field()
    contact = serpy.Field()
    country_id_bill_to = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    credits = serpy.MethodField()
    debits = serpy.MethodField()
    email_log = EmailLogSerializer(many=True, attr='email_log.all', call=True)
    id = serpy.Field()
    name_bill_to = serpy.Field()
    narrative = serpy.Field()
    postcode_bill_to = serpy.Field()
    report_template_id = serpy.Field()
    subdivision_id_bill_to = serpy.Field()
    transaction_date = serpy.Field(attr='transaction_date.isoformat', call=True)
    transaction_type_id = serpy.Field()
    tsn = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)

    # Backwards Compatibility (mostly needed for `Reporting` templates)
    old_address_id = serpy.Field(attr='address_id', label='idAddress')
    old_address1_bill_to = serpy.Field(attr='address1_bill_to', label='address1BillTo')
    old_address2_bill_to = serpy.Field(attr='address2_bill_to', label='address2BillTo')
    old_address3_bill_to = serpy.Field(attr='address3_bill_to', label='address3BillTo')
    old_city_bill_to = serpy.Field(attr='city_bill_to', label='cityBillTo')
    old_country_id_bill_to = serpy.Field(attr='country_id_bill_to', label='idCountryBillTo')
    old_email_log = EmailLogSerializer(many=True, attr='email_log.all', call=True, label='emailLog')
    old_name_id_bill_to = serpy.Field(attr='name_bill_to', label='companyNameBillTo')
    old_postcode_bill_to = serpy.Field(attr='postcode_bill_to', label='postcodeBillTo')
    old_subdivision_id_bill_to = serpy.Field(attr='subdivision_id_bill_to', label='idSubdivisionBillTo')
    old_transaction_date = serpy.Field(attr='transaction_date.isoformat', call=True, label='transactionDate')
    old_transaction_type_id = serpy.Field(attr='transaction_type_id', label='idTransactionType')
    old_tsn = serpy.Field(attr='tsn', label='transactionSequenceNumber')

    def __init__(self, *args, **kwargs):
        super(JournalEntrySerializer, self).__init__(*args, **kwargs)
        self.context = kwargs.get('context', dict())

        # Gather the account numbers from all the `debit` and `credit` records to be serialized so we can fetch all
        # the account names in one query
        if self.many:
            # Here self.instance is a queryset
            entries = self.instance
        else:
            # Otherwise, self.instance is one object
            entries = [self.instance]

        account_numbers = set()
        for entry in entries:
            for line in chain(entry.debits.all(), entry.credits.all()):
                account_numbers.add(line.nominal_account_number)

        if len(account_numbers) > 0:
            # Get Address Nominal Account descriptions
            accounts = AddressNominalAccount.objects.filter(
                address_id=entries[0].address_id,
                global_nominal_account__nominal_account_number__in=account_numbers,
            ).values('global_nominal_account__nominal_account_number', 'description')

            # Iterate through the accounts and make a dict of the values
            account_names = dict()
            for a in accounts.iterator():
                account_names[a['global_nominal_account__nominal_account_number']] = a['description']
            self.context['account_names'] = account_names

    def get_credits(self, obj):
        return NominalLedgerLineSerializer(instance=obj.credits.all(), many=True, context=self.context).data

    def get_debits(self, obj):
        return NominalLedgerLineSerializer(instance=obj.debits.all(), many=True, context=self.context).data
