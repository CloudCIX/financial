"""
Error Codes for all of the Methods in the Global Nominal Account service
"""

# List
financial_nominal_contra_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns.'
)

# Create
financial_nominal_contra_create_101 = (
    'The "global_nominal_account_id" parameter is invalid. "global_nominal_account_id" is required and must be an '
    'integer.'
)
financial_nominal_contra_create_102 = (
    'The "global_nominal_account_id" parameter is invalid. "global_nominal_account_id" must belong to a valid Global '
    'Nominal Account record within your Member.'
)
financial_nominal_contra_create_103 = (
    'The "global_nominal_account_id" parameter is invalid. Nominal Contras can only be set up for Nominal Accounts'
    ' which have Account Numbers in the range 1000 to 2999 inclusive.'
)
financial_nominal_contra_create_104 = (
    'The "payment_method_id" parameter is invalid. "payment_method_id" is required and must be an integer.'
)
financial_nominal_contra_create_105 = (
    'The "payment_method_id" parameter is invalid. "payment_method_id" must belong to a valid Payment Method record '
    'within your Member.'
)
financial_nominal_contra_create_106 = (
    'The "transaction_type_id" parameter is invalid. "transaction_type_id" is required and must be an integer.'
)
financial_nominal_contra_create_107 = (
    'The "transaction_type_id" parameter is invalid. The supported values for "transaction_type_id" are 10000, 10001, '
    '10004, 11000, 11001, 11004.'
)
financial_nominal_contra_create_108 = (
    'The "transaction_type_id" parameter is invalid. This "transaction_type_id" and "payment_method_id" pair is '
    'already in use.'
)
financial_nominal_contra_create_201 = (
    'You do not have permission to make this request. Your Member must be self-managed.'
)
financial_nominal_contra_create_202 = (
    'You do not have permission to make this request. You must be an administrator to create a Nominal Contra.'
)

# Read
financial_nominal_contra_read_001 = (
    'The "pk" path parameter is invalid. "pk" must belong to a valid Nominal Contra record.'
)

# Update
financial_nominal_contra_update_001 = (
    'The "pk" path parameter is invalid. "pk" must belong to a valid Nominal Contra record.'
)
financial_nominal_contra_update_101 = (
    'The "global_nominal_account_id" parameter is invalid. "global_nominal_account_id" is required and must be an '
    'integer.'
)
financial_nominal_contra_update_102 = (
    'The "global_nominal_account_id" parameter is invalid. "global_nominal_account_id" must belong to a valid Nominal '
    'Contra record.'
)
financial_nominal_contra_update_103 = (
    'The "global_nominal_account_id" parameter is invalid. Nominal Contras can only be set up for Nominal Accounts'
    ' which have Account Numbers in the range 1000 to 2999 inclusive.'
)
financial_nominal_contra_update_104 = (
    'The "payment_method_id" parameter is invalid. "payment_method_id" is required and must be an integer.'
)
financial_nominal_contra_update_105 = (
    'The "payment_method_id" parameter is invalid. "payment_method_id" must belong to a valid Payment Method record.'
)
financial_nominal_contra_update_106 = (
    'The "transaction_type_id" parameter is invalid. "transaction_type_id" is required and must be an integer.'
)
financial_nominal_contra_update_107 = (
    'The "transaction_type_id" parameter is invalid. The supported values for "transaction_type_id" are 10000, 10001, '
    '10004, 11000, 11001, 11004.'
)
financial_nominal_contra_update_108 = (
    'The "payment_method_id" and "transaction_type_id" parameters are invalid. There is already a Nominal Contra set '
    'up in your Member with this combination of "payment_method_id" and "transaction_type_id".'
)
financial_nominal_contra_update_201 = (
    'You do not have permission to make this request. Your Member must be self-managed.'
)
financial_nominal_contra_update_202 = (
    'You do not have permission to make this request. You must be an administrator to update a Nominal Contra record.'
)

# Delete
financial_nominal_contra_delete_001 = (
    'The "pk" path parameter is invalid. "pk" must belong to a valid Nominal Contra record.'
)
financial_nominal_contra_delete_201 = (
    'You do not have permission to make this request. Your Member must be self-managed.'
)
financial_nominal_contra_delete_202 = (
    'You do not have permission to make this request. You must be an administrator to delete a Nominal Contra record.'
)
