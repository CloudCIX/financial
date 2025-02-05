# libs
import serpy
# local
from financial.serializers.global_nominal_account import GlobalNominalAccountSerializer
from financial.serializers.payment_method import PaymentMethodSerializer


__all__ = [
    'NominalContraSerializer',
]


class NominalContraSerializer(serpy.Serializer):
    """
    created:
        description: Timestamp, in ISO format, of when the Nominal Contra record was created.
        type: string
    global_nominal_account:
        $ref: '#/components/schemas/GlobalNominalAccount'
    id:
        description: The id of the Nominal Contra record.
        type: integer
    payment_method:
        $ref: '#/components/schemas/PaymentMethod'
    transaction_type_id:
        description: The id of one of the Transaction Types supported by CloudCIX.
        type: integer
    updated:
        description: Timestamp, in ISO format, of when the Nominal Contra record was last updated.
        type: string
    uri:
        description: The absolute URL of the Nominal Contra that can be used to perform `Read` and `Update` operations.
        type: string
    """
    created = serpy.Field(attr='created.isoformat', call=True)
    global_nominal_account = GlobalNominalAccountSerializer()
    id = serpy.Field()
    payment_method = PaymentMethodSerializer()
    transaction_type_id = serpy.Field()
    updated = serpy.Field(attr='updated.isoformat', call=True)
    uri = serpy.Field(attr='get_absolute_url', call=True)

    # Backwards compatibility
    old_nominal_account = GlobalNominalAccountSerializer(attr='global_nominal_account', label='nominalAccount')
    old_nominal_account_id = serpy.Field(attr='global_nominal_account_id', label='idNominalAccount')
    old_payment_method = PaymentMethodSerializer(attr='payment_method', label='paymentMethod')
    old_payment_method_id = serpy.Field(attr='payment_method_id', label='idPaymentMethod')
    old_transaction_type_id = serpy.Field(attr='transaction_type_id', label='idTransactionType')
