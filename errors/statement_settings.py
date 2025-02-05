"""
Error Codes for all of the Methods in the Statement Setting service
"""
financial_statement_settings_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns.'
)
# Read
financial_statement_settings_read_201 = (
    'You do not have permission to make this request. You can only read the Statement Settings for your own Address.'
)
# Update
financial_statement_settings_update_101 = 'The "day" parameter is invalid. "day" must be an array.'
financial_statement_settings_update_102 = (
    'The "day" parameter is invalid. All items in the array "day" must be an integer.'
)
financial_statement_settings_update_103 = (
    'The "day" parameter is invalid. All items in the array "day" must be an integer between 1 and 31.'
)
financial_statement_settings_update_104 = 'The "min_credit" parameter is invalid. "min_credit"  must be a decimal.'
financial_statement_settings_update_105 = (
    'The "min_credit" parameter is invalid. "min_credit"  must be a decimal less than 0.'
)
financial_statement_settings_update_106 = 'The "min_debit" parameter is invalid. "min_debit"  must be a decimal.'
financial_statement_settings_update_107 = (
    'The "min_debit" parameter is invalid. "min_debit"  must be a decimal greater than 0.'
)
financial_statement_settings_update_108 = (
    'The "reply_to" parameter is invalid. One or more of emails provided is not a valid email'
)

financial_statement_settings_update_201 = (
    'You do not have permission to make this request. Your Member must be self-managed.'
)
financial_statement_settings_update_202 = (
    'You do not have permission to make this request. You can only update the Statement Settings for your own Address.'
)
