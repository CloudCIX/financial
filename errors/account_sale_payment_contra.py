"""
Error Codes for all of the Methods in the Account Sale Payment Contra service
"""

from . import default

# Create
financial_account_sale_payment_contra_create_001 = (
    'The "source_id" path parameter is invalid. "source_id" must be the id of a valid Address that your Address is '
    'linked to.'
)
financial_account_sale_payment_contra_create_101 = default.narrative__too_long
financial_account_sale_payment_contra_create_102 = default.report_template_id__not_int
financial_account_sale_payment_contra_create_103 = default.report_template_id__invalid_id
financial_account_sale_payment_contra_create_104 = (
    'The "report_template_id" parameter is invalid. The Report Template must be for Account Sale Payments.'
)
financial_account_sale_payment_contra_create_105 = default.transaction_date__not_isoformat
financial_account_sale_payment_contra_create_106 = default.transaction_date__period_ended
financial_account_sale_payment_contra_create_107 = default.tsn__required_int
financial_account_sale_payment_contra_create_108 = (
    'The "tsn" parameter is invalid. "tsn" must belong to a valid Account Purchase Payment in the Address specified by '
    'the "source_id".'
)
financial_account_sale_payment_contra_create_109 = (
    'The "tsn" parameter is invalid. An Account Sale Payment has already been made from the Account Purchase Payment '
    'specified by "tsn".'
)
financial_account_sale_payment_contra_create_110 = (
    'The "payment_method_id" parameter is invalid. "payment_method_id" is required and must be an int.'
)
financial_account_sale_payment_contra_create_111 = (
    'The "payment_method_id" parameter is invalid. "payment_method_id" must belong to a valid Payment Method in your '
    'Member.'
)
financial_account_sale_payment_contra_create_112 = (
    'The "payment_method_id" parameter is invalid. There is no Nominal Contra set up to specify which Nominal Account '
    'to debit when creating an Account Sale Payment with the specified Payment Method.'
)
financial_account_sale_payment_contra_create_113 = (
    'The "payment_method_id" parameter is invalid. The Nominal Account specified by the nominal Contra does not have '
    'an Address Nominal Account set up for your Address.'
)
financial_account_sale_payment_contra_create_114 = (
    'The "payment_method_id" parameter is invalid. The Nominal Account specified by the Nominal Contra does not have '
    'a Nominal Account Number in the allowed range, 1000 to 2999 inclusive.'
)
financial_account_sale_payment_contra_create_115 = (
    'The "payment_method_id" parameter is invalid. The Nominal Account specified by the Nominal Contra uses a '
    'different currency to the currency that the Purchase Payment was made with.'
)
financial_account_sale_payment_contra_create_116 = (
    'The "exchange_rate" parameter is invalid. The Purchase Payment was conducted in a different currency to your '
    'Address\'s currency so an "exchange_rate" is required and must be a decimal string.'
)
financial_account_sale_payment_contra_create_201 = default.not_self_managed

# Read
financial_account_sale_payment_contra_read_001 = (
    'The "tsn" and/or "source_id" path parameters are invalid. The Address specified by "source_id" has no Account '
    'Sale Payment with the specified "tsn".'
)
financial_account_sale_payment_contra_read_201 = (
    'You do not have permission to make this request. This Account Sale Payment does not reference your Address.'
)
