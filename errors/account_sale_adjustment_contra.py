"""
Error Codes for all of the Methods in the Account Sale Adjustment Contra service
"""

from . import default

# Create
financial_account_sale_adjustment_contra_create_001 = (
    'The "source_id" path parameter is invalid. "source_id" must be the id of a valid Address that your Address is '
    'linked to.'
)
financial_account_sale_adjustment_contra_create_101 = default.narrative__too_long
financial_account_sale_adjustment_contra_create_102 = default.report_template_id__not_int
financial_account_sale_adjustment_contra_create_103 = default.report_template_id__invalid_id
financial_account_sale_adjustment_contra_create_104 = (
    'The "report_template_id" parameter is invalid. The Report Template must be for Account Sales Adjustments.'
)
financial_account_sale_adjustment_contra_create_105 = default.transaction_date__not_isoformat
financial_account_sale_adjustment_contra_create_106 = default.transaction_date__period_ended
financial_account_sale_adjustment_contra_create_107 = default.tsn__required_int
financial_account_sale_adjustment_contra_create_108 = (
    'The "tsn" parameter is invalid. "tsn" must belong to a valid Account Purchase Adjustment in the Address specified '
    'by the "source_id".'
)
financial_account_sale_adjustment_contra_create_109 = (
    'The "tsn" parameter is invalid. An Account Sale Adjustment has already been created from the Account Purchase '
    'Adjustment specified by "tsn".'
)
financial_account_sale_adjustment_contra_create_110 = (
    'The "tsn" parameter is invalid. The Transaction Date of the Account Purchase Adjustment with this "tsn" is after '
    'the "transaction_date" provided for creating an Account Sale Adjustment.'
)
financial_account_sale_adjustment_contra_create_111 = (
    'The "debit" parameter is invalid. "debit" is required and must be a dictionary containing a decimal "amount", and '
    'a "number" for a Nominal Account in your Address.'
)
financial_account_sale_adjustment_contra_create_112 = (
    'The "debit" parameter is invalid. "debit" must contain an "amount" which must be a string in decimal format.'
)
financial_account_sale_adjustment_contra_create_113 = (
    'The "debit" parameter is invalid. "debit" must contain a "number" value, which must be a valid Nominal Account '
    'Number within your Address.'
)
financial_account_sale_adjustment_contra_create_114 = (
    'The "debit" parameter is invalid. The debit "amount" must equal the credit amount from the Account Purchase '
    'Adjustment.'
)
financial_account_sale_adjustment_contra_create_115 = (
    'The "debit" parameter is invalid. The Account Purchase Adjustment credited the Creditor Control Account, so this '
    'transaction needs to debit the Debtor Control Account.'
)
financial_account_sale_adjustment_contra_create_116 = (
    'The "debit" parameter is invalid. There is no Nominal Account in your Address with the "number" specified by '
    '"debit".'
)
financial_account_sale_adjustment_contra_create_117 = (
    'The "credit" parameter is invalid. "credit" is required and must be a dictionary containing a decimal "amount", '
    'and a "number" for a Nominal Account in your Address.'
)
financial_account_sale_adjustment_contra_create_118 = (
    'The "credit" parameter is invalid. "credit" must contain an "amount" which must be a string in decimal format.'
)
financial_account_sale_adjustment_contra_create_119 = (
    'The "credit" parameter is invalid. "credit" must contain a "number" value, which must be a valid Nominal Account '
    'Number within your Address.'
)
financial_account_sale_adjustment_contra_create_120 = (
    'The "credit" parameter is invalid. The credit "amount" must equal the debit amount from the Account Purchase '
    'Adjustment.'
)
financial_account_sale_adjustment_contra_create_121 = (
    'The "credit" parameter is invalid. The Account Purchase Adjustment debited the Creditor Control Account, so this '
    'transaction needs to credit the Debtor Control Account.'
)
financial_account_sale_adjustment_contra_create_122 = (
    'The "credit" parameter is invalid. There is no Sales Nominal Account in your Address with the "number" specified '
    'by "debit".'
)
financial_account_sale_adjustment_contra_create_201 = default.not_self_managed

# Read
financial_account_sale_adjustment_contra_read_001 = (
    'The "tsn" and/or "source_id" path parameters are invalid. The Address specified by "source_id" has no Account '
    'Sale Adjustments with the specified "tsn".'
)
financial_account_sale_adjustment_contra_read_201 = (
    'You do not have permission to make this request. This Account Sale Adjustment does not reference your Address.'
)
