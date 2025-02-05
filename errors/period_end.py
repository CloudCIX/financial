"""
Error Codes for all of the Methods in the Period End service
"""

from . import default

# List
financial_period_end_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns.'
)

# Create
financial_period_end_create_101 = default.narrative__too_long
financial_period_end_create_102 = default.transaction_date__not_isoformat
financial_period_end_create_103 = (
    'The "transaction_date" parameter is invalid. "transaction_date" cannot be a date in the future.'
)
financial_period_end_create_104 = default.transaction_date__period_ended
financial_period_end_create_105 = (
    'The "transaction_date" parameter is invalid. The total debits and credits from all transactions from the last '
    'period end to "transaction_date" do not equal.'
)
financial_period_end_create_201 = default.not_self_managed

# Read
financial_period_end_read_001 = (
    'The "tsn" path parameter is invalid. "tsn" must be a valid Transaction Sequence Number for a Period End in your '
    'Address.'
)

# Delete
financial_period_end_delete_001 = (
    'The "tsn" path parameter is invalid. "tsn" must be a valid Transaction Sequence Number for a Period End in your '
    'Address.'
)
financial_period_end_delete_201 = (
    'You do not have permission to make this request. Only the most recent Period End in an Address can be deleted.'
)
financial_period_end_delete_202 = (
    'You do not have permission to make this request. This Period End is connected to a Year End record and so cannot '
    'be deleted.'
)
