"""
Error Codes for all of the Methods in the Global Nominal Account service
"""

# List
financial_global_nominal_account_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns.'
)

# Create
financial_global_nominal_account_create_101 = (
    'The "description" parameter is invalid. "description" is required and must be a string.'
)
financial_global_nominal_account_create_102 = (
    'The "description" parameter is invalid. "description" is required and cannot be longer than 100 characters.'
)
financial_global_nominal_account_create_103 = (
    'The "description" parameter is invalid. A Nominal Account exists in this Member with the given "description".'
)
financial_global_nominal_account_create_104 = (
    'The "nominal_account_type_id" parameter is invalid. "nominal_account_type_id" is required and must be an integer.'
)
financial_global_nominal_account_create_105 = (
    'The "nominal_account_type_id" parameter is invalid. "nominal_account_type_id" must belong to a valid Nominal '
    'Account Type.'
)
financial_global_nominal_account_create_106 = (
    'The "nominal_account_number" parameter is invalid. "nominal_account_number" is required and must be an integer.'
)
financial_global_nominal_account_create_107 = (
    'The "nominal_account_number" parameter is invalid. "nominal_account_number" is required and must be between the '
    'valid numbers defined by the Nominal Account Type.'
)
financial_global_nominal_account_create_108 = (
    'The "nominal_account_number" parameter is invalid. A Nominal Account with this "nominal_account_number" already '
    'exists in this Member.'
)
financial_global_nominal_account_create_109 = (
    'The "external_reference" parameter is invalid. "external_reference" cannot be longer than 50 characters.'
)
financial_global_nominal_account_create_110 = (
    'The "external_reference" parameter is invalid. A Nominal Account with this "external_reference" already exists '
    'in this Member.'
)
financial_global_nominal_account_create_111 = (
    'The "currency_id" parameter is invalid. "currency_id" is required and must be an integer'
)
financial_global_nominal_account_create_112 = (
    'The "currency_id" parameter is invalid. "currency_id" must belong to a valid Currency.'
)
financial_global_nominal_account_create_113 = (
    'The "valid_sales_account" parameter is invalid. "valid_sales_account" must be a boolean.'
)
financial_global_nominal_account_create_114 = (
    'The "valid_purchases_account" parameter is invalid. "valid_purchases_account" must be a boolean.'
)
financial_global_nominal_account_create_201 = (
    'You do not have permission to make this request. Your Member must be self-managed.'
)
financial_global_nominal_account_create_202 = (
    'You do not have permission to make this request. You must be an administrator to create a Global Nominal Account.'
)

# Read
financial_global_nominal_account_read_001 = 'The "address_id" parameter is invalid. "address_id" must be an integer.'
financial_global_nominal_account_read_002 = (
    'The "pk" path parameter is invalid. "pk" must belong to a valid Global Nominal Account record.'
)

# Update
financial_global_nominal_account_update_001 = (
    'The "pk" path parameter is invalid. "pk" must belong to a valid Global Nominal Account record.'
)
financial_global_nominal_account_update_101 = 'The "address_id" parameter is invalid. "address_id" must be an integer.'
financial_global_nominal_account_update_102 = (
    'The "description" parameter is invalid. "description" is required and must be a string.'
)
financial_global_nominal_account_update_103 = (
    'The "description" parameter is invalid. "description" cannot be longer than 100 characters.'
)
financial_global_nominal_account_update_104 = (
    'The "description" parameter is invalid. A Nominal Account in this Address already exists with this "description".'
)
financial_global_nominal_account_update_105 = (
    'The "description" parameter is invalid. A Nominal Account in this Member already exists with this "description".'
)
financial_global_nominal_account_update_106 = (
    'The "external_reference" parameter is invalid. "external_reference" cannot be longer than 50 characters.'
)
financial_global_nominal_account_update_107 = (
    'The "external_reference" parameter is invalid. A Nominal Account with this "external_reference" already exists in '
    'this Member.'
)
financial_global_nominal_account_update_108 = (
    'The "currency_id" parameter is invalid. "currency_id" is required and must be an integer.'
)
financial_global_nominal_account_update_109 = (
    'The "currency_id" parameter is invalid. "currency_id" must belong to a valid Currency.'
)
financial_global_nominal_account_update_110 = (
    'The "valid_sales_account" parameter is invalid. "valid_sales_account" must be a boolean.'
)
financial_global_nominal_account_update_111 = (
    'The "valid_purchases_account" parameter is invalid. "valid_purchases_account" must be a boolean.'
)
financial_global_nominal_account_update_201 = (
    'You do not have permission to make this request. You must be an Administrator to update Nominal Account records.'
)
financial_global_nominal_account_update_202 = (
    'You do not have permission to make this request. To update a Nominal Account for an Address you must be operating '
    'in that Address.'
)

# Delete
financial_global_nominal_account_delete_001 = (
    'The "pk" path parameter is invalid. "pk" must belong to a valid Global Nominal Account record.'
)
financial_global_nominal_account_delete_002 = 'The "address_id" parameter is invalid. "address_id" must be an integer.'
financial_global_nominal_account_delete_003 = (
    'The "address_id" parameter is invalid. There is no Address Nominal Account with this"address_id".'
)
financial_global_nominal_account_delete_201 = (
    'You do not have permission to make this request. Your Member must be self-managed.'
)
financial_global_nominal_account_delete_202 = (
    'You do not have permission to make this request. You must be an Administrator to delete Nominal Account records.'
)
financial_global_nominal_account_delete_203 = (
    'You do not have permission to make this request. You cannot delete a Global nominal Account from another Member.'
)
financial_global_nominal_account_delete_204 = (
    'You do not have permission to make this request. This is one of the default accounts set up by the Financial '
    'Application. Deleting this account will cause services to stop working.'
)
financial_global_nominal_account_delete_205 = (
    'You do not have permission to make this request. An Address in your Member has already used this Nominal Account '
    'in a transaction.'
)
