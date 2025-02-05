"""
Error Codes for all of the Methods in the Cash Sale Invoice Contra service
"""

from . import default

# Create
financial_cash_sale_invoice_contra_create_001 = ()
financial_cash_sale_invoice_contra_create_101 = default.payment_method_id__required_int
financial_cash_sale_invoice_contra_create_102 = default.payment_method_id__invalid_id
financial_cash_sale_invoice_contra_create_103 = (
    'The "payment_method_id" parameter is invalid. There is no Nominal Contra set up to specify which Nominal Account '
    'to debit when making a Cash Sale Invoice with the specified Payment Method.'
)
financial_cash_sale_invoice_contra_create_104 = default.payment_method_id__no_address_account
financial_cash_sale_invoice_contra_create_105 = (
    'The "payment_method_id" parameter is invalid. The Nominal Account specified by the Nominal Contra does not have a '
    'Nominal Account Number in the allowed range, 1000 to 2999 inclusive.'
)
financial_cash_sale_invoice_contra_create_106 = default.report_template_id__not_int
financial_cash_sale_invoice_contra_create_107 = default.report_template_id__invalid_id
financial_cash_sale_invoice_contra_create_108 = (
    'The "report_template_id" parameter is invalid. The Report Template must be for Cash Sale Invoices.'
)
financial_cash_sale_invoice_contra_create_109 = default.transaction_date__not_isoformat
financial_cash_sale_invoice_contra_create_110 = default.transaction_date__period_ended
financial_cash_sale_invoice_contra_create_111 = default.tsn__required_int
financial_cash_sale_invoice_contra_create_112 = (
    'The "tsn" parameter is invalid. "tsn" must belong to a valid Cash Purchase Invoice in the Address specified by '
    'the "source_id".'
)
financial_cash_sale_invoice_contra_create_113 = (
    'The "tsn" parameter is invalid. A Cash Sale Invoice has already been created from the Cash Purchase Invoice '
    'specified by "tsn".'
)
financial_cash_sale_invoice_contra_create_114 = default.lines__not_list
financial_cash_sale_invoice_contra_create_115 = (
    'The "lines" parameter is invalid. There must be one less line than there are debits in the Cash Purchase Invoice. '
    'A Nominal Ledger entry will automatically be created for the tax on the transaction.'
)
financial_cash_sale_invoice_contra_create_116 = default.lines_items__not_dict
financial_cash_sale_invoice_contra_create_117 = default.lines_description__required_string
financial_cash_sale_invoice_contra_create_118 = default.lines_exchange_rate__not_decimal
financial_cash_sale_invoice_contra_create_119 = default.lines_number__out_of_range
financial_cash_sale_invoice_contra_create_120 = default.lines_number__required_int
financial_cash_sale_invoice_contra_create_121 = default.lines_quantity__required_decimal
financial_cash_sale_invoice_contra_create_122 = default.lines_tax_rate_id__required_int
financial_cash_sale_invoice_contra_create_123 = default.lines_unit_price__required_decimal
financial_cash_sale_invoice_contra_create_124 = default.lines_number__invalid_account
financial_cash_sale_invoice_contra_create_125 = default.lines_number__required_sales
financial_cash_sale_invoice_contra_create_126 = default.lines_tax_rate_id__invalid_id
financial_cash_sale_invoice_contra_create_127 = (
    'The "lines" parameter is invalid. One of the credits does not match any of the debits on the Cash Purchase '
    'Invoice.'
)
financial_cash_sale_invoice_contra_create_128 = default.lines_description__too_long
financial_cash_sale_invoice_contra_create_201 = default.not_self_managed

# Read
financial_cash_sale_invoice_contra_read_001 = (
    'The "tsn" and/or "source_id" path parameters are invalid. The Address specified by "source_id" has no Cash Sale '
    'Invoice with the specified "tsn".'
)
financial_cash_sale_invoice_contra_read_201 = (
    'You do not have permission to make this request. This Cash Sale Invoice does not reference your Address.'
)
