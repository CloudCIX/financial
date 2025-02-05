"""
Error Codes for all of the Methods in the Account Purchase Debit Note service
"""

# local
from . import default

# Create
financial_account_purchase_debit_note_create_101 = default.address1_deliver_to__required_string
financial_account_purchase_debit_note_create_102 = default.address1_deliver_to__too_long
financial_account_purchase_debit_note_create_103 = default.address2_deliver_to__too_long
financial_account_purchase_debit_note_create_104 = default.address3_deliver_to__too_long
financial_account_purchase_debit_note_create_105 = default.city_deliver_to__required_string
financial_account_purchase_debit_note_create_106 = default.city_deliver_to__too_long
financial_account_purchase_debit_note_create_107 = default.contra_address_id__required_int
financial_account_purchase_debit_note_create_108 = default.contra_address_id__invalid_id
financial_account_purchase_debit_note_create_109 = default.contra_contact_id__not_int
financial_account_purchase_debit_note_create_110 = default.contra_contact_id__invalid_id
financial_account_purchase_debit_note_create_111 = default.country_id_deliver_to__required_int
financial_account_purchase_debit_note_create_112 = default.country_id_deliver_to__invalid_id
financial_account_purchase_debit_note_create_113 = default.external_reference__too_long
financial_account_purchase_debit_note_create_114 = default.lines__not_list
financial_account_purchase_debit_note_create_115 = default.lines_items__not_dict
financial_account_purchase_debit_note_create_116 = default.lines_description__required_string
financial_account_purchase_debit_note_create_117 = default.lines_exchange_rate__not_decimal
financial_account_purchase_debit_note_create_118 = default.lines_number__out_of_range
financial_account_purchase_debit_note_create_119 = default.lines_number__required_int
financial_account_purchase_debit_note_create_120 = default.lines_quantity__required_decimal
financial_account_purchase_debit_note_create_121 = default.lines_tax_amount__not_decimal
financial_account_purchase_debit_note_create_122 = default.lines_tax_rate_id__required_int
financial_account_purchase_debit_note_create_123 = default.lines_unit_price__required_decimal
financial_account_purchase_debit_note_create_124 = default.lines_number__invalid_account
financial_account_purchase_debit_note_create_125 = (
    'The "lines" parameter is invalid. Each item in "lines" must contain a Nominal Account "number" referencing a '
    'Purchase Account in your Address, or the VAT Control Account.'
)
financial_account_purchase_debit_note_create_126 = default.lines_tax_rate_id__invalid_id
financial_account_purchase_debit_note_create_127 = default.lines_tax_amount__incorrectly_calculated
financial_account_purchase_debit_note_create_128 = default.lines__negative_total
financial_account_purchase_debit_note_create_129 = default.name_deliver_to__required_string
financial_account_purchase_debit_note_create_130 = default.name_deliver_to__too_long
financial_account_purchase_debit_note_create_131 = default.narrative__too_long
financial_account_purchase_debit_note_create_132 = default.postcode_deliver_to__too_long
financial_account_purchase_debit_note_create_133 = default.report_template_id__not_int
financial_account_purchase_debit_note_create_134 = default.report_template_id__invalid_id
financial_account_purchase_debit_note_create_135 = (
    'The "report_template_id" parameter is invalid. The Report Template must be for Account Purchase Debit Notes.'
)
financial_account_purchase_debit_note_create_136 = default.subdivision_id_deliver_to__not_int
financial_account_purchase_debit_note_create_137 = default.subdivision_id_deliver_to__invalid_id
financial_account_purchase_debit_note_create_138 = default.transaction_date__not_isoformat
financial_account_purchase_debit_note_create_139 = default.transaction_date__period_ended
financial_account_purchase_debit_note_create_140 = default.lines_description__too_long
financial_account_purchase_debit_note_create_201 = default.not_self_managed

# Read
financial_account_purchase_debit_note_read_001 = (
    'The "tsn" path parameter is invalid. "tsn" must be a valid Transaction Sequence Number for an Account Purchase '
    'Debit Note.'
)
financial_account_purchase_debit_note_read_201 = (
    'You do not have permission to make this request. You cannot read an Account Purchase Debit Note that does not '
    'reference your Address.'
)

# Update
financial_account_purchase_debit_note_update_001 = (
    'The "tsn" path parameter is invalid. "tsn" must be a valid Transaction Sequence Number for an Account Purchase '
    'Debit Note within your Address.'
)
financial_account_purchase_debit_note_update_101 = default.external_reference__too_long
financial_account_purchase_debit_note_update_201 = (
    'You do not have permission to make this request. An Account Sale Credit Note has already been made from the '
    'information on this Account Purchase Debit Note.'
)
financial_account_purchase_debit_note_update_202 = (
    'You do not have permission to make this request. This Account Purchase Debit Note has already been processed by a '
    'period end.'
)
financial_account_purchase_debit_note_update_203 = (
    'You do not have permission to make this request. This Account Purchase Debit Note has already been allocated.'
)
