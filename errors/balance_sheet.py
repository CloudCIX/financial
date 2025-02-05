"""
Error Codes for all of the Methods in the Balance Sheet service
"""

# List
financial_balance_sheet_list_101 = 'The "address_id" parameter is invalid. "address_id" must be an integer.'
financial_balance_sheet_list_102 = (
    'The "date" parameter is invalid. "date" is required and must be a string in isoformat.'
)
financial_balance_sheet_list_201 = (
    'You do not have permission to make this request. You must be Global Active to make a Balance Sheet for another '
    'Address in your Member.'
)
financial_balance_sheet_list_202 = (
    'You do not have permission to make this request. You cannot make a Balance Sheet for an Address in another Member.'
)
