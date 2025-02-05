"""
Error Codes for all of the Methods in the Allocation service
"""
# List
financial_allocation_list_001 = (
    "'allocation_type' is a required search field. The value sent must be either 'supplier' or 'customer'"
)
financial_allocation_list_002 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns.'
)

# Create
financial_allocation_create_101 = (
    'The "allocations" parameter is invalid. "allocations" is required and must be a list.'
)
financial_allocation_create_102 = (
    'The "allocations" parameter is invalid. The number of allocations in the list must be greater than zero.'
)
financial_allocation_create_103 = (
    'The "allocations" parameter is invalid. Each item in "allocations" must be a dictionary.'
)
financial_allocation_create_104 = (
    'The "allocations" parameter is invalid. Each item in "allocations" must contain an "amount" string in'
    'decimal format.'
)
financial_allocation_create_105 = (
    'The "allocations" parameter is invalid. One of the items in "allocations" uses a "tsn" that is not an integer.'
)
financial_allocation_create_106 = (
    'The "allocations" parameter is invalid. One of the items in "allocations" uses a "transaction_type_id" '
    ' that is not an integer.'
)
financial_allocation_create_107 = (
    'The "allocations" parameter is invalid. One of the items in "allocations" uses a "transaction_type_id"'
    'that is not a valid Sales Account or Purchases Account.'
)
financial_allocation_create_108 = (
    'The "allocations" parameter is invalid. One of the items in "allocations" uses a "transaction_type_id"'
    'that does not match a a valid Sales Account.'
)
financial_allocation_create_109 = (
    'The "allocations" parameter is invalid. One of the items in "allocations" uses a "transaction_type_id"'
    'that does not match a a valid Purchases Account.'
)
financial_allocation_create_110 = (
    'The "allocations" parameter is invalid. One of the items in "allocations" uses a "nominal_ledger_id" that '
    'does not exist for the supplied "transaction_type_id" and your Address'
)
financial_allocation_create_111 = (
    'The "allocations" parameter is invalid. Each item in "allocations" must contain a "nominal_ledger" transaction '
    'for the same "contra_address_id".'
)
financial_allocation_create_112 = (
    'The "allocations" parameter is invalid. One of the items in "allocations" uses an "amount" that will increase '
    'the "unallocated_balance" of the "nominal_ledger_id" provided'
)
financial_allocation_create_113 = (
    'The "allocations" parameter is invalid. One of the items in "allocations" uses an "amount" that is larger than '
    'the "unallocated_balance" of the "nominal_ledger_id" provided'
)
financial_allocation_create_114 = (
    'The "allocations" parameter is invalid. One of the items in "allocations" uses an "amount" that will decrease '
    'the "unallocated_balance" of the "nominal_ledger_id" provided further'
)
financial_allocation_create_115 = (
    'The "allocations" parameter is invalid. One of the items in "allocations" uses an "amount" that is less than '
    'the "unallocated_balance" of the "nominal_ledger_id" provided'
)
financial_allocation_create_116 = (
    'The "allocations" parameter is invalid. One of the items in "allocations" uses a "nominal_ledger_id" that has no '
    '"unallocated_balance" to rectify'
)
financial_allocation_create_117 = (
    'The balance total of all the allocations must be zero.'
)
financial_allocation_create_201 = 'You do not have permission to execute this method. Your Member must be self-managed.'


# Delete
financial_allocation_delete_001 = 'The "pk" path parameter is invalid. "pk" must belong to a valid Allocation record.'
financial_allocation_delete_201 = (
    'You do not have permission to make this request. You can only delete an Allocation record from your own Address.'
)
