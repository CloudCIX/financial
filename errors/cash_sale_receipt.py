"""
Error Codes for all of the Methods in the Cash Sale Receipt service
"""

from . import default

# Create
financial_cash_sale_receipt_create_101 = default.address1_bill_to__too_long
financial_cash_sale_receipt_create_102 = default.address1_deliver_to__too_long
financial_cash_sale_receipt_create_103 = default.address2_bill_to__too_long
financial_cash_sale_receipt_create_104 = default.address2_deliver_to__too_long
financial_cash_sale_receipt_create_105 = default.address3_bill_to__too_long
financial_cash_sale_receipt_create_106 = default.address3_deliver_to__too_long
financial_cash_sale_receipt_create_107 = default.city_bill_to__too_long
financial_cash_sale_receipt_create_108 = default.city_deliver_to__too_long
financial_cash_sale_receipt_create_109 = default.contra_contact__too_long
financial_cash_sale_receipt_create_110 = default.country_id_deliver_to__not_int
financial_cash_sale_receipt_create_111 = default.country_id_deliver_to__invalid_id
financial_cash_sale_receipt_create_112 = default.external_reference__too_long
financial_cash_sale_receipt_create_113 = default.name_bill_to__too_long
financial_cash_sale_receipt_create_114 = default.name_deliver_to__too_long
financial_cash_sale_receipt_create_115 = default.narrative__too_long
financial_cash_sale_receipt_create_116 = default.postcode_bill_to__too_long
financial_cash_sale_receipt_create_117 = default.postcode_deliver_to__too_long
financial_cash_sale_receipt_create_118 = default.subdivision_id_deliver_to__not_int
financial_cash_sale_receipt_create_119 = default.subdivision_id_deliver_to__invalid_id
financial_cash_sale_receipt_create_120 = default.transaction_date__not_isoformat
financial_cash_sale_receipt_create_121 = default.transaction_date__period_ended
financial_cash_sale_receipt_create_122 = default.lines__not_list
financial_cash_sale_receipt_create_123 = default.lines_items__not_dict
financial_cash_sale_receipt_create_124 = default.lines_description__required_string
financial_cash_sale_receipt_create_125 = default.lines_description__too_long
financial_cash_sale_receipt_create_126 = default.lines_exchange_rate__not_decimal
financial_cash_sale_receipt_create_127 = default.lines_number__out_of_range
financial_cash_sale_receipt_create_128 = default.lines_number__required_int
financial_cash_sale_receipt_create_129 = default.lines_quantity__required_decimal
financial_cash_sale_receipt_create_130 = default.lines_tax_rate_id__required_int
financial_cash_sale_receipt_create_131 = default.lines_unit_price__required_decimal
financial_cash_sale_receipt_create_132 = default.lines_number__invalid_account
financial_cash_sale_receipt_create_133 = default.lines_number__required_sales
financial_cash_sale_receipt_create_134 = default.lines_tax_rate_id__invalid_id
financial_cash_sale_receipt_create_135 = default.lines__negative_total
financial_cash_sale_receipt_create_136 = default.payment_method_id__required_int
financial_cash_sale_receipt_create_137 = default.payment_method_id__invalid_id
financial_cash_sale_receipt_create_138 = (
    'The "payment_method_id" parameter is invalid. There is no Nominal Contra set up to specify which Nominal Account '
    'to credit when making a Cash Purchase Receipt with the specified Payment Method.'
)
financial_cash_sale_receipt_create_139 = default.payment_method_id__no_address_account
financial_cash_sale_receipt_create_140 = (
    'The "payment_method_id" parameter is invalid. The Nominal Account specified by the Nominal Contra does not have a '
    'Nominal Account Number in the allowed range, 1000 to 2999 inclusive.'
)
financial_cash_sale_receipt_create_141 = default.report_template_id__not_int
financial_cash_sale_receipt_create_142 = default.report_template_id__invalid_id
financial_cash_sale_receipt_create_143 = (
    'The "report_template_id" parameter is invalid. The Report Template must be for Cash Sale Receipts.'
)
financial_cash_sale_receipt_create_201 = default.not_self_managed

# Read
financial_cash_sale_receipt_read_001 = (
    'The "tsn" path parameter is invalid. "tsn" must be a valid Transaction Sequence Number for a Cash Sale Receipt in'
    ' your Address.'
)

# Update
financial_cash_sale_receipt_update_001 = (
    'The "tsn" path parameter is invalid. "tsn" must be a valid Transaction Sequence Number for a Cash Sale Receipt in'
    ' your Address.'
)
financial_cash_sale_receipt_update_101 = default.address1_bill_to__too_long
financial_cash_sale_receipt_update_102 = default.address1_deliver_to__too_long
financial_cash_sale_receipt_update_103 = default.address2_bill_to__too_long
financial_cash_sale_receipt_update_104 = default.address2_deliver_to__too_long
financial_cash_sale_receipt_update_105 = default.address3_bill_to__too_long
financial_cash_sale_receipt_update_106 = default.address3_deliver_to__too_long
financial_cash_sale_receipt_update_107 = default.city_bill_to__too_long
financial_cash_sale_receipt_update_108 = default.city_deliver_to__too_long
financial_cash_sale_receipt_update_109 = default.contra_contact__too_long
financial_cash_sale_receipt_update_110 = default.country_id_deliver_to__not_int
financial_cash_sale_receipt_update_111 = default.country_id_deliver_to__invalid_id
financial_cash_sale_receipt_update_112 = default.external_reference__too_long
financial_cash_sale_receipt_update_113 = default.name_bill_to__too_long
financial_cash_sale_receipt_update_114 = default.name_deliver_to__required_string
financial_cash_sale_receipt_update_115 = default.narrative__too_long
financial_cash_sale_receipt_update_116 = default.postcode_bill_to__too_long
financial_cash_sale_receipt_update_117 = default.postcode_deliver_to__too_long
financial_cash_sale_receipt_update_118 = default.subdivision_id_deliver_to__not_int
financial_cash_sale_receipt_update_119 = default.subdivision_id_deliver_to__no_country_id
financial_cash_sale_receipt_update_120 = default.subdivision_id_deliver_to__invalid_id
financial_cash_sale_receipt_update_201 = (
    'You do not have permission to make this request. This Cash Sale Receipt has already been processed by a period '
    'end.'
)
