"""
Error Codes for all of the Methods in the Year End service
"""

# local
from . import default

# List
financial_year_end_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns.'
)

# Create
financial_year_end_create_101 = default.narrative__too_long
financial_year_end_create_102 = default.transaction_date__not_isoformat
financial_year_end_create_103 = (
    'The "transaction_date" parameter is invalid. "transaction_date" cannot be a date in the future.'
)
financial_year_end_create_104 = default.transaction_date__period_ended
financial_year_end_create_105 = (
    'The "transaction_date" parameter is invalid. The outstanding balance in the Suspense Account (Account Number '
    '7999) must be zero on the date of a Year End transaction.'
)
financial_year_end_create_106 = (
    'The "transaction_date" parameter is invalid. The total debits and credits from all transactions from the last '
    'Year End to "transaction_date" do not equal.'
)
financial_year_end_create_201 = default.not_self_managed

# Read
financial_year_end_read_001 = (
    'The "tsn" path parameter is invalid. "tsn" must be a valid Transaction Sequence Number for a Year End in your '
    'Address.'
)

# Delete
financial_year_end_delete_001 = (
    'The "tsn" path parameter is invalid. "tsn" must be a valid Transaction Sequence Number for a Year End in your '
    'Address.'
)
financial_year_end_delete_201 = (
    'You do not have permission to make this request. Year End has already been processed by a Period End.'
)
