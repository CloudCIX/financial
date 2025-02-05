# libs
import serpy
# local
from financial.serializers.nominal_account_type import NominalAccountTypeSerializer


__all__ = [
    'GlobalNominalAccountSerializer',
]


class GlobalNominalAccountSerializer(serpy.Serializer):
    """
    address_id:
        description: An optional field of the id of the Address that a Nominal Account belongs to
        type: integer
    currency_id:
        description: The id of the Currency that this Global Nominal Account uses
        type: integer
    description:
        description: What transactions are recorded in the Global Nominal Account
        type: string
    external_reference:
        description: |
            For Users migrating from Sage, External Reference is the Account Number that they previously used for this
            account.
        type: string
    id:
        description: The id of the Global Nominal Account record
        type: integer
    member_id:
        description: The id of the Member that this Global Nominal Account belongs to
        type: integer
    nominal_account_number:
        description: |
            A number to identify what kind of transactions an account can be used for. Unique within a Member's list of
            Global accounts.
        type: integer
    nominal_account_type:
        $ref: '#/components/schemas/NominalAccountType'
    uri:
        description: |
            The absolute URL of the Global Nominal Account that can be used to perform `Read` and `Update` operations on
            it
        type: string
    valid_sales_account:
        description: Whether this account can be used for sales transactions
        type: boolean
    valid_purchases_account:
        description: Whether this account can be used for purchases transactions
        type: boolean
    """
    address_id = serpy.MethodField()
    currency_id = serpy.Field()
    description = serpy.Field()
    external_reference = serpy.Field()
    id = serpy.Field()
    member_id = serpy.Field()
    nominal_account_number = serpy.Field()
    nominal_account_type = NominalAccountTypeSerializer()
    uri = serpy.Field(attr='get_absolute_url', call=True)
    valid_sales_account = serpy.Field()
    valid_purchases_account = serpy.Field()

    def get_address_id(self, obj):
        return getattr(obj, 'address_id', None)

    # Backwards Compatibility
    old_currency_id = serpy.Field(attr='currency_id', label='idCurrency')
    old_id = serpy.Field(attr='id', label='idNominalAccount')
    old_member_id = serpy.Field(attr='member_id', label='idMember')
    old_nominal_account_number = serpy.Field(attr='nominal_account_number', label='number')
    old_nominal_account_type_id = serpy.Field(attr='nominal_account_type_id', label='idNominalAccountType')
    old_reference = serpy.Field(attr='external_reference', label='reference')
    old_valid_purchases_account = serpy.Field(attr='valid_purchases_account', label='validPurchasesAccount')
    old_valid_sales_account = serpy.Field(attr='valid_sales_account', label='validSalesAccount')
