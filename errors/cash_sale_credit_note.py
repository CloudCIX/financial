"""
Error Codes for all of the Methods in the Cash Sale Credit Note service
"""

# local
from . import default

# Create
financial_cash_sale_credit_note_create_101 = default.address1_deliver_to__required_string
financial_cash_sale_credit_note_create_102 = default.address1_deliver_to__too_long
financial_cash_sale_credit_note_create_103 = default.address2_deliver_to__too_long
financial_cash_sale_credit_note_create_104 = default.address3_deliver_to__too_long
financial_cash_sale_credit_note_create_105 = default.city_deliver_to__required_string
financial_cash_sale_credit_note_create_106 = default.city_deliver_to__too_long
financial_cash_sale_credit_note_create_107 = default.contra_address_id__required_int
financial_cash_sale_credit_note_create_108 = default.contra_address_id__invalid_id
financial_cash_sale_credit_note_create_109 = default.contra_contact_id__not_int
financial_cash_sale_credit_note_create_110 = default.contra_contact_id__invalid_id
financial_cash_sale_credit_note_create_111 = default.country_id_deliver_to__required_int
financial_cash_sale_credit_note_create_112 = default.country_id_deliver_to__invalid_id
financial_cash_sale_credit_note_create_113 = default.external_reference__too_long
financial_cash_sale_credit_note_create_114 = default.lines__not_list
financial_cash_sale_credit_note_create_115 = default.lines_items__not_dict
financial_cash_sale_credit_note_create_116 = default.lines_description__required_string
financial_cash_sale_credit_note_create_117 = default.lines_exchange_rate__not_decimal
financial_cash_sale_credit_note_create_118 = default.lines_number__out_of_range
financial_cash_sale_credit_note_create_119 = default.lines_number__required_int
financial_cash_sale_credit_note_create_120 = default.lines_quantity__required_decimal
financial_cash_sale_credit_note_create_121 = default.lines_tax_rate_id__required_int
financial_cash_sale_credit_note_create_122 = default.lines_unit_price__required_decimal
financial_cash_sale_credit_note_create_123 = default.lines_number__invalid_account
financial_cash_sale_credit_note_create_124 = (
    'The "lines" parameter is invalid. Each item in "lines" must contain a Nominal Account "number" referencing a '
    'Sales Account in your Address, or the VAT Control Account.'
)
financial_cash_sale_credit_note_create_125 = default.lines_tax_rate_id__invalid_id
financial_cash_sale_credit_note_create_126 = default.lines__negative_total
financial_cash_sale_credit_note_create_127 = default.name_deliver_to__required_string
financial_cash_sale_credit_note_create_128 = default.name_deliver_to__too_long
financial_cash_sale_credit_note_create_129 = default.narrative__too_long
financial_cash_sale_credit_note_create_130 = default.payment_method_id__required_int
financial_cash_sale_credit_note_create_131 = default.payment_method_id__invalid_id
financial_cash_sale_credit_note_create_132 = (
    'The "payment_method_id" parameter is invalid. There is no Nominal Contra set up to specify which Nominal Account '
    'to credit when making a Cash Sale Credit Note with the specified Payment Method.'
)
financial_cash_sale_credit_note_create_133 = default.payment_method_id__no_address_account
financial_cash_sale_credit_note_create_134 = (
    'The "payment_method_id" parameter is invalid. The Nominal Account specified by the Nominal Contra does not have a '
    'Nominal Account Number in the allowed range, 1000 to 2999 inclusive.'
)
financial_cash_sale_credit_note_create_135 = default.postcode_deliver_to__too_long
financial_cash_sale_credit_note_create_136 = default.report_template_id__not_int
financial_cash_sale_credit_note_create_137 = default.report_template_id__invalid_id
financial_cash_sale_credit_note_create_138 = (
    'The "report_template_id" parameter is invalid. The Report Template must be for Cash Sale Credit Notes.'
)
financial_cash_sale_credit_note_create_139 = default.subdivision_id_deliver_to__not_int
financial_cash_sale_credit_note_create_140 = default.subdivision_id_deliver_to__invalid_id
financial_cash_sale_credit_note_create_141 = default.transaction_date__not_isoformat
financial_cash_sale_credit_note_create_142 = default.transaction_date__period_ended
financial_cash_sale_credit_note_create_143 = default.lines_description__too_long
financial_cash_sale_credit_note_create_201 = default.not_self_managed

# Read
financial_cash_sale_credit_note_read_001 = (
    'The "tsn" path parameter is invalid. "tsn" must be a valid Transaction Sequence Number of an Cash Sale Credit '
    'Note in your Address.'
)
financial_cash_sale_credit_note_read_002 = (
    'The "address_id" parameter is invalid. "address_id" must be an integer corresponding to the id of an Address in '
    'your Member.'
)
financial_cash_sale_credit_note_read_201 = (
    'You do not have permission to make this request. You cannot read a Cash Sale Credit Note that does not reference '
    'your Address.'
)

# Update
financial_cash_sale_credit_note_update_001 = (
    'The "tsn" path parameter is invalid. "tsn" must be a valid Transaction Sequence Number for a Cash Sale Credit '
    'Note in your Address.'
)
financial_cash_sale_credit_note_update_101 = default.external_reference__too_long
financial_cash_sale_credit_note_update_201 = (
    'You do not have permission to make this request. A Cash Purchase Debit Note has already been made from the '
    'information on this Cash Sale Credit Note.'
)
financial_cash_sale_credit_note_update_202 = (
    'You do not have permission to make this request. This Cash Sale Credit Note has already been processed by a '
    'period end.'
)
financial_cash_sale_credit_note_update_203 = (
    'You do not have permission to make this request. This Cash Sale Credit Note has already been allocated.'
)
