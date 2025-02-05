"""
Error Codes for all of the Methods in the Account Purchase Debit Note service
"""

# local
from . import default

# Create
financial_account_purchase_debit_note_contra_create_001 = (
    'The "source_id" path parameter is invalid. "source_id" must be the id of a valid Address that your Address is '
    'linked to.'
)
financial_account_purchase_debit_note_contra_create_101 = default.narrative__too_long
financial_account_purchase_debit_note_contra_create_102 = default.report_template_id__not_int
financial_account_purchase_debit_note_contra_create_103 = default.report_template_id__invalid_id
financial_account_purchase_debit_note_contra_create_104 = (
    'The "report_template_id" parameter is invalid. The Report Template must be for Account Purchase Debit Notes.'
)
financial_account_purchase_debit_note_contra_create_105 = default.transaction_date__not_isoformat
financial_account_purchase_debit_note_contra_create_106 = default.transaction_date__period_ended
financial_account_purchase_debit_note_contra_create_107 = default.tsn__required_int
financial_account_purchase_debit_note_contra_create_108 = (
    'The "tsn" parameter is invalid. "tsn" must be a valid Transaction Sequence Number for an Account Sale Credit Note '
    'in the Address specified by the "source_id".'
)
financial_account_purchase_debit_note_contra_create_109 = (
    'The "tsn" parameter is invalid. An Account Purchase Debit Note has already been created from the Account Sale '
    'Credit Note specified by "tsn".'
)
financial_account_purchase_debit_note_contra_create_110 = default.lines__not_list
financial_account_purchase_debit_note_contra_create_111 = (
    'The "lines" parameter is invalid. There must be one less line than there are debits in the Account Sale Credit '
    'Note. A Nominal Ledger entry will automatically be created for the tax on the transaction.'
)
financial_account_purchase_debit_note_contra_create_112 = default.lines_items__not_dict
financial_account_purchase_debit_note_contra_create_113 = default.lines_description__required_string
financial_account_purchase_debit_note_contra_create_114 = default.lines_exchange_rate__not_decimal
financial_account_purchase_debit_note_contra_create_115 = default.lines_number__out_of_range
financial_account_purchase_debit_note_contra_create_116 = default.lines_number__required_int
financial_account_purchase_debit_note_contra_create_117 = default.lines_quantity__required_decimal
financial_account_purchase_debit_note_contra_create_118 = default.lines_tax_rate_id__required_int
financial_account_purchase_debit_note_contra_create_119 = default.lines_unit_price__required_decimal
financial_account_purchase_debit_note_contra_create_120 = default.lines_number__invalid_account
financial_account_purchase_debit_note_contra_create_121 = default.lines_number__required_purchases
financial_account_purchase_debit_note_contra_create_122 = default.lines_tax_rate_id__invalid_id
financial_account_purchase_debit_note_contra_create_123 = (
    'The "lines" parameter is invalid. One of the lines does not match any of the debits on the Account Sale Credit '
    'Note.'
)
financial_account_purchase_debit_note_contra_create_124 = default.lines_description__too_long
financial_account_purchase_debit_note_contra_create_201 = default.not_self_managed

# Read
financial_account_purchase_debit_note_contra_read_001 = (
    'The "tsn" and/or "source_id" path parameters are invalid. The Address specified by "source_id" has no Account '
    'Purchase Debit Notes with the specified "tsn".'
)
financial_account_purchase_debit_note_contra_read_201 = (
    'You do not have permission to make this request. This Account Purchase Debit Note does not reference your Address.'
)
