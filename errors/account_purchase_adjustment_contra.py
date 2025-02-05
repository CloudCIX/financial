"""
Error Codes for all of the Methods in the Account Purchase Adjustment Contra service
"""

# Create
financial_account_purchase_adjustment_contra_create_001 = (
    'The "source_id" path parameter is invalid. "source_id" must be the id of a valid Address that your Address is '
    'linked to.'
)
financial_account_purchase_adjustment_contra_create_101 = (
    'The "narrative" parameter is invalid. "narrative" cannot be longer than 250 characters.'
)
financial_account_purchase_adjustment_contra_create_102 = (
    'The "report_template_id" parameter is invalid. "report_template_id" must be an integer.'
)
financial_account_purchase_adjustment_contra_create_103 = (
    'The "report_template_id" parameter is invalid. "report_template_id" must belong to a valid Report Template.'
)
financial_account_purchase_adjustment_contra_create_104 = (
    'The "report_template_id" parameter is invalid. The Report Template must be for Account Purchase Adjustments.'
)
financial_account_purchase_adjustment_contra_create_105 = (
    'The "transaction_date" parameter is invalid. "transaction_date" is required and must be a date string in '
    'isoformat.'
)
financial_account_purchase_adjustment_contra_create_106 = (
    'The "transaction_date" parameter is invalid. This "transaction_date" has already been processed by a Period End.'
)
financial_account_purchase_adjustment_contra_create_107 = (
    'The "tsn" parameter is invalid. "tsn" is required and must be an integer.'
)
financial_account_purchase_adjustment_contra_create_108 = (
    'The "tsn" parameter is invalid. "tsn" must be a valid Transaction Sequence Number for an Account Sale Adjustment '
    'in the Address specified by the "source_id".'
)
financial_account_purchase_adjustment_contra_create_109 = (
    'The "tsn" parameter is invalid. An Account Purchase Adjustment has already been created from the Account Sale '
    'Adjustment specified by "tsn".'
)
financial_account_purchase_adjustment_contra_create_110 = (
    'The "tsn" parameter is invalid. The Transaction Date of the Account Sale Adjustment with this "tsn" is after '
    'the "transaction_date" provided for creating an Account Purchase Adjustment.'
)
financial_account_purchase_adjustment_contra_create_111 = (
    'The "debit" parameter is invalid. "debit" is required and must be a dictionary containing a decimal "amount", and '
    'a "number" for a Nominal Account in your Address.'
)
financial_account_purchase_adjustment_contra_create_112 = (
    'The "debit" parameter is invalid. "debit" must contain an "amount" which must be a string in decimal format.'
)
financial_account_purchase_adjustment_contra_create_113 = (
    'The "debit" parameter is invalid. "debit" must contain a "number" value, which must be a valid Nominal Account '
    'Number within your Address.'
)
financial_account_purchase_adjustment_contra_create_114 = (
    'The "debit" parameter is invalid. The debit "amount" must equal the credit amount from the Account Sale '
    'Adjustment.'
)
financial_account_purchase_adjustment_contra_create_115 = (
    'The "debit" parameter is invalid. The Account Sale Adjustment credited the Debtor Control Account, so this '
    'transaction needs to debit the Creditor Control Account.'
)
financial_account_purchase_adjustment_contra_create_116 = (
    'The "debit" parameter is invalid. There is no Nominal Account in your Address with the "number" specified by '
    'the "debit".'
)
financial_account_purchase_adjustment_contra_create_117 = (
    'The "credit" parameter is invalid. "credit" is required and must be a dictionary containing a decimal "amount", '
    'and a "number" for a Nominal Account in your Address.'
)
financial_account_purchase_adjustment_contra_create_118 = (
    'The "credit" parameter is invalid. "credit" must contain an "amount" which must be a string in decimal format.'
)
financial_account_purchase_adjustment_contra_create_119 = (
    'The "credit" parameter is invalid. "credit" must contain a "number" value, which must be a valid Nominal Account '
    'Number within your Address.'
)
financial_account_purchase_adjustment_contra_create_120 = (
    'The "credit" parameter is invalid. The credit "amount" must equal the debit amount from the Account Sale '
    'Adjustment.'
)
financial_account_purchase_adjustment_contra_create_121 = (
    'The "credit" parameter is invalid. The Account Sale Adjustment debited the Debtor Control Account, so this '
    'transaction needs to credit the Creditor Control Account.'
)
financial_account_purchase_adjustment_contra_create_122 = (
    'The "credit" parameter is invalid. There is no Nominal Account in your Address with the "number" specified by '
    'the "credit".'
)
financial_account_purchase_adjustment_contra_create_201 = (
    'You do not have permission to make this request. Your Member must be self-managed.'
)

# Read
financial_account_purchase_adjustment_contra_read_001 = (
    'The "tsn" and/or "source_id" path parameters are invalid. The Address specified by "source_id" has no Account '
    'Purchase Adjustments with the specified "tsn".'
)
financial_account_purchase_adjustment_contra_read_201 = (
    'You do not have permission to make this request. This Account Purchase Adjustment does not reference your Address.'
)
