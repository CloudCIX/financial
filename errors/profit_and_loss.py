"""
Error Codes for all of the Methods in the Profit and Loss service
"""

# List
financial_profit_and_loss_list_101 = 'The "address_id" parameter is invalid. "address_id" must be an integer.'
financial_profit_and_loss_list_102 = (
    'The "start_date" parameter is invalid. "start_date" is required and must be a date string in isoformat.'
)
financial_profit_and_loss_list_103 = (
    'The "end_date" parameter is invalid. "end_date" is required and must be a string in isoformat.'
)
financial_profit_and_loss_list_104 = 'The "end_date" parameter is invalid. "end_date" must be after "start_date".'
financial_profit_and_loss_list_201 = (
    'You do not have permission to make this request. You must be global active to list Profit and Loss data from '
    'other Addresses in your Member.'
)
financial_profit_and_loss_list_202 = (
    'You do not have permission to make this request. You cannot list  Profit and Loss data from an Address in another '
    'Member.'
)
