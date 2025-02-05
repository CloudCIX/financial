"""
Error Codes for all of the Methods in the Account Purchase Payment service
"""

from . import default

# Create
financial_account_purchase_payment_create_101 = (
    'The "amount" parameter is invalid. "amount" is required and must be a string in decimal format.'
)
financial_account_purchase_payment_create_102 = 'The "amount" parameter is invalid. "amount" must be positive.'
financial_account_purchase_payment_create_103 = default.contra_address_id__required_int
financial_account_purchase_payment_create_104 = default.contra_address_id__invalid_id
financial_account_purchase_payment_create_105 = default.narrative__too_long
financial_account_purchase_payment_create_106 = (
    'The "payment_method_id" parameter is invalid. "payment_method_id" is required and must be an integer.'
)
financial_account_purchase_payment_create_107 = (
    'The "payment_method_id" parameter is invalid. "payment_method_id" must belong to a valid Payment Method in your '
    'Member.'
)
financial_account_purchase_payment_create_108 = (
    'The "payment_method_id" parameter is invalid. There is no Nominal Contra set up to specify which Nominal Account '
    'to credit when making a Purchase Payment with the specified Payment Method.'
)
financial_account_purchase_payment_create_109 = (
    'The "payment_method_id" parameter is invalid. The Nominal Account specified by the Nominal Contra does not have a '
    'Nominal Account Number in the allowed range, 1000 to 2999 inclusive.'
)
financial_account_purchase_payment_create_110 = (
    'The "payment_method_id" parameter is invalid. The Nominal Account specified by the Nominal Contra does not have '
    'an Address Nominal Account set up for your Address.'
)
financial_account_purchase_payment_create_111 = default.report_template_id__not_int
financial_account_purchase_payment_create_112 = default.report_template_id__invalid_id
financial_account_purchase_payment_create_113 = (
    'The "report_template_id" parameter is invalid. The Report Template must be for Account Purchase Payments.'
)
financial_account_purchase_payment_create_114 = default.transaction_date__not_isoformat
financial_account_purchase_payment_create_115 = default.transaction_date__period_ended
financial_account_purchase_payment_create_116 = (
    'The "exchange_rate" parameter is invalid. The Account specified by the Payment Method uses a different currency '
    'to your Address so an "exchange_rate" is required and must be a decimal string.'
)
financial_account_purchase_payment_create_201 = default.not_self_managed

# Read
financial_account_purchase_payment_read_001 = (
    'The "tsn" path parameter is invalid. "tsn" must be a valid Transaction Sequence Number for an Account Purchase'
    'Payment within your Address.'
)
financial_account_purchase_payment_read_201 = (
    'You do not have permission to make this request. You cannot read an Account Purchase Payment that does not '
    'reference your Address.'
)
