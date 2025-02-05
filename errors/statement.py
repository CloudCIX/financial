"""
Error Codes for all of the Methods in the Statements service
"""

# Create
financial_statement_create_101 = 'The "address_id" parameter is invalid. "address_id" must be an integer.'
financial_statement_create_102 = 'The "address_id" parameter is invalid. "address_id" must be your Address.'
financial_statement_create_102 = 'You must set up Statement Settings for your Address before Statements can be sent.'
financial_statement_create_103 = (
    'The "address_id" parameter is invalid. "address_id" must belong to a valid Address record.'
)
financial_statement_create_104 = 'The "contra_address_id" parameter is invalid. "contra_address_id" is required.'
financial_statement_create_105 = (
    'The "contra_address_id" parameter is invalid. "contra_address_id" must be an integer.'
)
