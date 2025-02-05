# libs
import serpy


__all__ = [
    'NominalAccountTypeSerializer',
]


class NominalAccountTypeSerializer(serpy.Serializer):
    """
    description:
        description: What the Nominal Account Type is used for
        type: string
    max_account_number:
        description: All Nominal Accounts of this type have a Nominal Account Number less than Max Account Number
        type: integer
    min_account_number:
        description: All Nominal Accounts of this type have a Nominal Account Number greater than Min Account Number
        type: integer

    """
    description = serpy.Field()
    max_account_number = serpy.Field()
    min_account_number = serpy.Field()

    # Backwards Compatibility
    old_max_account_number = serpy.Field(attr='max_account_number', label='maxAccountNumber')
    old_min_account_number = serpy.Field(attr='min_account_number', label='id')
