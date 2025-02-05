"""
Error Codes for all of the Methods in the Account Purchase Adjustment service
"""

# Create
financial_account_purchase_adjustment_create_101 = (
    'The "contra_address_id" parameter is invalid. "contra_address_id" is required and must be an integer.'
)
financial_account_purchase_adjustment_create_102 = (
    'The "contra_address_id" parameter is invalid. You must be linked to an Address to create an Account Purchase '
    'Adjustment with it.'
)
financial_account_purchase_adjustment_create_103 = (
    'The "narrative" parameter is invalid. "narrative" cannot be longer than 250 characters.'
)
financial_account_purchase_adjustment_create_104 = (
    'The "report_template_id" parameter is invalid. "report_template_id" must be an integer.'
)
financial_account_purchase_adjustment_create_105 = (
    'The "report_template_id" parameter is invalid. "report_template_id" must belong to a valid Report Template.'
)
financial_account_purchase_adjustment_create_106 = (
    'The "report_template_id" parameter is invalid. The Report Template must be for Account Purchase Adjustments.'
)
financial_account_purchase_adjustment_create_107 = (
    'The "transaction_date" parameter is invalid. "transaction_date" is required and must be a date string in '
    'isoformat.'
)
financial_account_purchase_adjustment_create_108 = (
    'The "transaction_date" parameter is invalid. This "transaction_date" has already been processed by a Period End.'
)
financial_account_purchase_adjustment_create_109 = (
    'The "debit" parameter is invalid. "debit" is required and must be a dictionary containing a decimal "amount", and '
    'a "number" for a Nominal Account in your Address.'
)
financial_account_purchase_adjustment_create_110 = (
    'The "debit" parameter is invalid. "debit" must contain an "amount" which must be a string in decimal format.'
)
financial_account_purchase_adjustment_create_111 = (
    'The "debit" parameter is invalid. "debit" must contain a non-zero "amount" value.'
)
financial_account_purchase_adjustment_create_112 = (
    'The "debit" parameter is invalid. "debit" must contain a "number" value, which must be a valid Nominal Account '
    'Number within your Address.'
)
financial_account_purchase_adjustment_create_113 = (
    'The "debit" parameter is invalid. "debit" refers to the Debtor Control Account, which cannot be used when '
    'creating an Account Purchase Adjustment.'
)
financial_account_purchase_adjustment_create_114 = (
    'The "debit" parameter is invalid. "debit" refers to a Nominal Account Number that does not exist in your Address.'
)
financial_account_purchase_adjustment_create_115 = (
    'The "credit" parameter is invalid. "credit" is required and must be a dictionary containing a decimal "amount", '
    'and a "number" from a Nominal Account in your Address.'
)
financial_account_purchase_adjustment_create_116 = (
    'The "credit" parameter is invalid. "credit" must contain an "amount" which must be a string in decimal format.'
)
financial_account_purchase_adjustment_create_117 = (
    'The "credit" parameter is invalid. "credit" must contain a non-zero "amount" value.'
)
financial_account_purchase_adjustment_create_118 = (
    'The "credit" parameter is invalid. "credit" must contain a "number" value, which must be a valid Nominal Account '
    'Number within your Address.'
)
financial_account_purchase_adjustment_create_119 = (
    'The "credit" parameter is invalid. "credit" refers to the Debtor Control Account, which cannot be used when '
    'creating an Account Purchase Adjustment.'
)
financial_account_purchase_adjustment_create_120 = (
    'The "credit" parameter is invalid. "credit" refers to Nominal Account Number that does not exist in your Address.'
)
financial_account_purchase_adjustment_create_121 = (
    'The "credit" and/or "debit" parameters are invalid. The "debit" and "credit" must use different Nominal Account '
    '"numbers".'
)
financial_account_purchase_adjustment_create_122 = (
    'The "credit" and/or "debit" parameters are invalid. The Creditor Control Account must be debited or credited in '
    'an Account Purchase Adjustment.'
)
financial_account_purchase_adjustment_create_123 = (
    'The "credit" and/or "debit" parameters are invalid. The "amount" values from the "debit" and "credit" must equal.'
)
financial_account_purchase_adjustment_create_201 = (
    'You do not have permission to execute this method. Your Member must be self-managed.'
)

# Read
financial_account_purchase_adjustment_read_001 = (
    'The "tsn" path parameter is invalid. "tsn" must be a valid Transaction Sequence Number for an Account Purchase '
    'Adjustment in you Address.'
)

# Update
financial_account_purchase_adjustment_update_001 = (
    'The "tsn" path parameter is invalid. "tsn" must be a valid Transaction Sequence Number for an Account Purchase '
    'Adjustment in you Address.'
)
financial_account_purchase_adjustment_update_101 = (
    'The "report_template_id" parameter is invalid. "report_template_id" must be an integer.'
)
financial_account_purchase_adjustment_update_102 = (
    'The "report_template_id" parameter is invalid. "report_template_id" must belong to a valid Report Template.'
)
financial_account_purchase_adjustment_update_103 = (
    'The "report_template_id" parameter is invalid. The Report Template must be for Account Purchase Adjustments.'
)
