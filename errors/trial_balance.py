"""
Error Codes for all of the Methods in the Trial Balance service
"""

# List
financial_trial_balance_list_101 = 'The "address_id" parameter is invalid. "address_id" must be an integer.'
financial_trial_balance_list_102 = (
    'The "date" parameter is invalid. "date" is required and must be a date string in isoformat.'
)
financial_trial_balance_list_201 = (
    'You do not have permission to make this request. You must be global active to list Trial Balance data from other '
    'Addresses in your Member.'
)
financial_trial_balance_list_202 = (
    'You do not have permission to make this request. You cannot list Trial Balance data from an Address in another '
    'Member.'
)
