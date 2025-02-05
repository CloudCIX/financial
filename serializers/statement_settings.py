# libs
import serpy


__all__ = [
    'StatementSettingsSerializer',
]


class StatementSettingsSerializer(serpy.Serializer):
    """
    address_id:
        description: The id of the Address that the Statement Setting record belongs to
        type: integer
    day:
        description: The dates in each month that the statement will be sent out on
        type: array
        items:
            type: integer
    min_credit:
        description: |
            The minimum amount of the credit balance required on a clients account for a statemnt to be sent to.
        type: string
        format: decimal
    min_debit:
        description: |
            The minimum amount of the debit balance required on a clients account for a statemnt to be sent to.
        type: string
        format: decimal
    reply_to:
        description: |
            The email addresses for recipeints to reply to. Both 'Name <email@address.com>' and 'email@address.com'
            formats are supported seperated by commas.
        type: string
    signature:
        description: |
            The signature to be appended onto the end of the email.
        type: string
    """
    address_id = serpy.Field()
    day = serpy.Field()
    min_credit = serpy.Field()
    min_debit = serpy.Field()
    reply_to = serpy.Field()
    signature = serpy.Field()
