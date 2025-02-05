"""
Error Codes for all of the Methods in the Purchases by Country service
"""

# List
financial_purchases_by_country_list_101 = 'The "address_id" parameter is invalid. "address_id" must be an integer.'
financial_purchases_by_country_list_102 = (
    'The "start_date" parameter is invalid. "start_date" must be a string in isoformat.'
)
financial_purchases_by_country_list_103 = (
    'The "finish_date" parameter is invalid. "finish_date" must be a string in isoformat.'
)
financial_purchases_by_country_list_104 = (
    'The "finish_date" parameter is invalid. "finish_date" must be after the "start_date" provided.'
)

financial_purchases_by_country_list_201 = (
    'You do not have permission to make this request. You must be Global Active to list Purchases by Country for '
    'another Address in your Member.'
)
financial_purchases_by_country_list_202 = (
    'You do not have permission to make this request. You cannot list Purchases by Country for an Address in another '
    'Member.'
)
