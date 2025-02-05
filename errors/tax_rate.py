"""
Error Codes for all of the Methods in the Tax Rate service
"""

# List
financial_tax_rate_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns.'
)

# Create
financial_tax_rate_create_101 = (
    'The "description" parameter is invalid. "description" is required and must be a string.'
)
financial_tax_rate_create_102 = (
    'The "description" parameter is invalid. "description" cannot be longer than 50 characters.'
)
financial_tax_rate_create_103 = (
    'The "description" parameter is invalid. A Tax Rate record already exists within your Address with this '
    'description.'
)
financial_tax_rate_create_104 = (
    'The "percent" parameter is invalid. "percent" is required and must be a string in decimal format.'
)
financial_tax_rate_create_201 = 'You do not have permission to make this request. Your Member must be self-managed.'

# Read
financial_tax_rate_read_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Tax Rate record.'
financial_tax_rate_read_201 = (
    'You do not have permission to make this request. You can only read a Tax Rate record from your Address.'
)

# Update
financial_tax_rate_update_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Tax Rate record.'
financial_tax_rate_update_101 = (
    'The "description" parameter is invalid. "description" is required and must be a string.'
)
financial_tax_rate_update_102 = (
    'The "description" parameter is invalid. "description" cannot be longer than 50 characters.'
)
financial_tax_rate_update_103 = (
    'The "description" parameter is invalid. A Tax Rate record already exists within your Address with this '
    'description.'
)
financial_tax_rate_update_104 = (
    'The "percent" parameter is invalid. "percent" is required and must be a string in decimal format.'
)
financial_tax_rate_update_201 = (
    'You do not have permission to make this request. You can only update a Tax Rate record from your own Address.'
)

# Delete
financial_tax_rate_delete_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Tax Rate record.'
financial_tax_rate_delete_201 = (
    'You do not have permission to make this request. You can only delete a Tax Rate record from your own Address.'
)
financial_tax_rate_delete_202 = (
    'You do not have permission to make this request. You cannot delete the last Tax Rate record in your Address.'
)
