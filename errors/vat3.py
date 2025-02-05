"""
Error Codes for all of the Methods in the VAT3 service
"""

# List
financial_vat3_list_001 = (
    'A Tax Rate record for exports at 0% could not be found in the Address of the requesting User. The VAT 3 report is '
    'calculated from transactions that use this Tax Rate.'
)
financial_vat3_list_101 = (
    'The "start_date" parameter is invalid. "start_date" is required and must be a date string in isoformat.'
)
financial_vat3_list_102 = (
    'The "end_date" parameter is invalid. "end_date" is required and must be a date string in isoformat.'
)
financial_vat3_list_103 = 'The "end_date" parameter is invalid. "end_date" must be after the "start_date".'
