# libs
import serpy
# local
from financial.models.address_nominal_account import AddressNominalAccount


__all__ = [
    'NominalLedgerLineSerializer',
]


class NominalLedgerLineSerializer(serpy.Serializer):
    """
    account_name:
        description: The description of the Nominal Account used for this transaction line
        type: string
    amount:
        description: The total monetary value of the transaction line
        type: string
        format: decimal
    created:
        description: The date that the transaction line was created
        type: string
    description:
        description: A summary of the part number that was used in the transaction
        type: string
    exchange_rate:
        description: The exchange rate to the currency of the User's Address at the time the transaction took place
        type: string
        format: decimal
    id:
        description: The id of the Nominal Ledger Debit/Credit object
        type: integer
    nominal_account_number:
        description: The Number of the Nominal Account that is debited or credited by the transaction line
        type: integer
    part_number:
        description: The part number of the SKU that was used in the transaction line
        type: integer
    quantity:
        description: How many copies of the part number were exchanged in the transaction
        type: string
        format: decimal
    tax_percent:
        description: The percent of Tax that was applied to the transaction line
        type: string
        format: decimal
    tax_rate_id:
        description: The id of the Tax Rate record that was used for the transaction line
        type: integer
    unit_price:
        description: The price of one item with the supplied part number
        type: string
        format: decimal
    updated:
        description: The date that the transaction line was last updated
        type: string
    """
    account_name = serpy.MethodField()
    amount = serpy.StrField()
    created = serpy.Field(attr='created.isoformat', call=True)
    description = serpy.Field()
    exchange_rate = serpy.StrField()
    id = serpy.Field()
    nominal_account_number = serpy.Field()
    part_number = serpy.Field()
    quantity = serpy.StrField()
    tax_percent = serpy.StrField()
    tax_rate_id = serpy.Field()
    unit_price = serpy.StrField()
    updated = serpy.Field(attr='updated.isoformat', call=True)

    # Backwards compatibility
    old_exchange_rate = serpy.StrField(attr='exchange_rate', label='exchangeRate')
    old_part_number = serpy.Field(attr='part_number', label='partNumber')
    old_tax_rate = serpy.StrField(attr='tax_percent', label='taxRate')
    old_unit_price = serpy.StrField(attr='unit_price', label='unitPrice')

    def __init__(self, *args, **kwargs):
        super(NominalLedgerLineSerializer, self).__init__(*args, **kwargs)
        self.context = kwargs.get('context', dict())

    def get_account_name(self, obj):
        """
        Fetch the Nominal Account name from context if it was sent. If not, retrieve the data from the db
        :param obj: The Nominal Ledger Line object being serialized
        :return: The name of a Nominal Account
        """
        if 'account_names' in self.context:
            return self.context['account_names'].get(obj.nominal_account_number, 'Unavailable')

        # Only try to check the db if no `account_names` were sent. If the account could be found, its data should have
        # been in `account_names`.
        try:  # pragma: no cover
            return AddressNominalAccount.objects.values_list(
                'description',
                flat=True,
            ).get(
                global_nominal_account__nominal_account_number=obj.nominal_account_number,
                address_id=obj.nominal_ledger.address_id,
            )
        except AddressNominalAccount.DoesNotExist:  # pragma: no cover
            return 'Unavailable'
