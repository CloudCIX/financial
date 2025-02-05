# libs
import serpy

__all__ = [
    'EmailLogSerializer',
]


class EmailLogSerializer(serpy.Serializer):
    """
    comment:
        description: The body of the email that was sent.
        type: string
    created:
        description: Timestamp, in ISO format, of when the Email Log record was created.
        type: string
    email_from:
        description: The email address of the sender of the email.
        type: string
    email_to:
        description: The email address of the recipient.
        type: string
    nominal_ledger_id:
        description: The id of the Nominal Ledger that prompted the creation of this Email Log.
        type: integer
    receiver_user_id:
        description: The id of the email recipient.
        type: integer
    sender_user_id:
        description: The id of the sender of the email.
        type: integer
    status:
        description: An identifier for whether the email was sent successfully or an error occurred.
        type: string
    """
    comment = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    email_from = serpy.Field()
    email_to = serpy.Field()
    nominal_ledger_id = serpy.Field()
    receiver_user_id = serpy.Field()
    sender_user_id = serpy.Field()
    status = serpy.Field()
