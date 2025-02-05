# stdlib
from itertools import chain
# libs
import serpy
# local
from financial.models.address_nominal_account import AddressNominalAccount
from financial.serializers.email_log import EmailLogSerializer
from financial.serializers.nominal_ledger_line import NominalLedgerLineSerializer


__all__ = [
    'NominalLedgerSerializer',
]


class NominalLedgerSerializer(serpy.Serializer):
    """
    address_id:
        description: The id of the Address that created the Nominal Ledger entry
        type: integer
    address1_bill_to:
        description: The first line of the address to bill for the transaction
        type: string
    address1_deliver_to:
        description: The first line of the address to deliver the transaction SKU items to
        type: string
    address2_bill_to:
        description: The second line of the address to bill for the transaction
        type: string
    address2_deliver_to:
        description: The second line of the address to deliver the transaction SKU items to
        type: string
    address3_bill_to:
        description: The third line of the address to bill for the transaction
        type: string
    address3_deliver_to:
        description: The third line of the address to deliver the transaction SKU items to
        type: string
    city_bill_to:
        description: The city in which the company to bill for the transaction line is located
        type: string
    city_deliver_to:
        description: The city in which the company to deliver the SKU items is located
        type: string
    contact:
        description: The name of the User who created the Nominal Ledger entry
        type: string
    contra_address_id:
        description: |
            The Address id of another Financial User who created a transaction between their own Address and the current
            User's Address
        type: integer
    contra_contact:
        description: |
            The name of another User of the Financial application that created a transaction with the current User's
            Address
        type: string
    contra_nominal_ledger_id:
        description: The id of the Nominal Ledger entry that was created in response to the current Transaction
        type: integer
    country_id_bill_to:
        description: The id of the Country in which the company to bill for the transaction is located
        type: integer
    country_id_deliver_to:
        description: The id of the Country in which the company to deliver the SKU items is located
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
    external_reference:
        description: The referencing system that the User's Member uses to track transactions
        type: string
    id:
        description: The id of the Nominal Ledger record
        type: integer
    name_bill_to:
        description: The name of the company that the transaction will be billed to
        type: string
    name_deliver_to:
        description: The name of the company that the transaction's SKU items will be delivered to
        type: integer
    narrative:
        description: A description of the transaction that created the Nominal Ledger entry
        type: string
    postcode_bill_to:
        description: The postcode of the company that the transaction will be billed to
        type: string
    postcode_deliver_to:
        description: The postcode of the company that the transaction's SKU items will be delivered to
        type: string
    report_template_id:
        description: The id of the Report Template to use when printing this Nominal Ledger entry
        type: integer
    subdivision_id_bill_to:
        description: The id of the Subdivision in which the company to bill for the transaction is located
        type: integer
    subdivision_id_deliver_to:
        description: The id of the Subdivision in which the company to deliver the SKU items is located
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
    unallocated_balance:
        description: The amount left unpaid on a transaction
        type: string
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
    address1_deliver_to = serpy.Field()
    address2_bill_to = serpy.Field()
    address2_deliver_to = serpy.Field()
    address3_bill_to = serpy.Field()
    address3_deliver_to = serpy.Field()
    city_bill_to = serpy.Field()
    city_deliver_to = serpy.Field()
    contact = serpy.Field()
    contra_address_id = serpy.Field()
    contra_contact = serpy.Field()
    contra_nominal_ledger_id = serpy.Field()
    country_id_bill_to = serpy.Field()
    country_id_deliver_to = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    credits = serpy.MethodField()
    debits = serpy.MethodField()
    external_reference = serpy.Field()
    email_log = EmailLogSerializer(many=True, attr='email_log.all', call=True)
    id = serpy.Field()
    name_bill_to = serpy.Field()
    name_deliver_to = serpy.Field()
    narrative = serpy.Field()
    postcode_bill_to = serpy.Field()
    postcode_deliver_to = serpy.Field()
    report_template_id = serpy.Field()
    subdivision_id_bill_to = serpy.Field()
    subdivision_id_deliver_to = serpy.Field()
    transaction_date = serpy.Field(attr='transaction_date.isoformat', call=True)
    transaction_type_id = serpy.Field()
    tsn = serpy.Field()
    unallocated_balance = serpy.StrField()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)

    # Backwards compatibility
    old_address_id = serpy.Field(attr='address_id', label='idAddress')
    old_address1_bill_to = serpy.Field(attr='address1_bill_to', label='address1BillTo')
    old_address1_deliver_to = serpy.Field(attr='address1_deliver_to', label='address1DeliverTo')
    old_address2_bill_to = serpy.Field(attr='address2_bill_to', label='address2BillTo')
    old_address2_deliver_to = serpy.Field(attr='address2_deliver_to', label='address2DeliverTo')
    old_address3_bill_to = serpy.Field(attr='address3_bill_to', label='address3BillTo')
    old_address3_deliver_to = serpy.Field(attr='address3_deliver_to', label='address3DeliverTo')
    old_city_bill_to = serpy.Field(attr='city_bill_to', label='cityBillTo')
    old_city_deliver_to = serpy.Field(attr='city_deliver_to', label='cityDeliverTo')
    old_contra_address_id = serpy.Field(attr='contra_address_id', label='idAddressContra')
    old_contra_contact = serpy.Field(attr='contra_contact', label='contraContact')
    old_contra_nominal_ledger_id = serpy.Field(attr='contra_nominal_ledger_id', label='idContraJournal')
    old_country_id_bill_to = serpy.Field(attr='country_id_bill_to', label='idCountryBillTo')
    old_country_id_deliver_to = serpy.Field(attr='country_id_deliver_to', label='idCountryDeliverTo')
    old_external_reference = serpy.Field(attr='external_reference', label='customerPONumber')
    old_name_bill_to = serpy.Field(attr='name_bill_to', label='companyNameBillTo')
    old_name_deliver_to = serpy.Field(attr='name_deliver_to', label='companyNameDeliverTo')
    old_postcode_bill_to = serpy.Field(attr='postcode_bill_to', label='postcodeBillTo')
    old_postcode_deliver_to = serpy.Field(attr='postcode_deliver_to', label='postcodeDeliverTo')
    old_report_template_id = serpy.Field(attr='report_template_id', label='idReportTemplate')
    old_subdivision_id_bill_to = serpy.Field(attr='subdivision_id_bill_to', label='idSubdivisionBillTo')
    old_subdivision_id_deliver_to = serpy.Field(attr='subdivision_id_deliver_to', label='idSubdivisionDeliverTo')
    old_transaction_type_id = serpy.Field(attr='transaction_type_id', label='idTransactionType')
    old_tsn = serpy.Field(attr='tsn', label='transactionSequenceNumber')
    old_transaction_date = serpy.Field(attr='transaction_date.isoformat', call=True, label='transactionDate')
    old_unallocated_balance = serpy.StrField(attr='unallocated_balance', label='unallocatedBalance')

    def __init__(self, *args, **kwargs):
        super(NominalLedgerSerializer, self).__init__(*args, **kwargs)
        self.context = kwargs.get('context', dict())

        if self.instance is not None:
            self.context['account_names'] = self.get_account_names()

    def get_account_names(self):
        # Gather the account numbers from all the `debit` and `credit` records to be serialized so we can fetch all
        # the account names in one query
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
