"""
Error Codes for all of the Methods in the Global Nominal Account service
"""

# List
financial_payment_method_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns.'
)

# Create
financial_payment_method_create_101 = (
    'The "description" parameter is invalid. "description" is required and must be a string.'
)
financial_payment_method_create_102 = (
    'The "description" parameter is invalid. "description" cannot be longer than 20 characters.'
)
financial_payment_method_create_103 = (
    'The "description" parameter is invalid. A Payment Method with this "description" already exists in this Member.'
)
financial_payment_method_create_201 = (
    'You do not have permission to make this request. Your Member must be self-managed.'
)
financial_payment_method_create_202 = (
    'You do not have permission to make this request. You must be an administrator to create a Payment Method.'
)

# Read
financial_payment_method_read_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Payment Method.'

# Update
financial_payment_method_update_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Payment Method.'
financial_payment_method_update_101 = (
    'The "description" parameter is invalid. "description" is required and must be a string.'
)
financial_payment_method_update_102 = (
    'The "description" parameter is invalid. "description" cannot be longer than 20 characters.'
)
financial_payment_method_update_103 = (
    'The "description" parameter is invalid. A Payment Method with this "description" already exists in this Member.'
)
financial_payment_method_update_201 = (
    'You do not have permission to make this request. Your Member must be self-managed.'
)
financial_payment_method_update_202 = (
    'You do not have permission to make this request. You must be an administrator to update a Payment Method.'
)

# Delete
financial_payment_method_delete_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Payment Method.'
financial_payment_method_delete_201 = (
    'You do not have permission to make this request. Your Member must be self-managed.'
)
financial_payment_method_delete_202 = (
    'You do not have permission to make this request. You must be an administrator to delete a Payment Method.'
)
financial_payment_method_delete_203 = (
    'You do not have permission to make this request. You cannot delete the last Payment Method in your Member.'
)
