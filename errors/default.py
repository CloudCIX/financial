"""
Error codes common to many views that use the Nominal Ledger model
"""

# Controller
address1_deliver_to__required_string = (
    'The "address1_deliver_to" parameter is invalid. "address1_deliver_to" is required and must be a string.'
)
address1_bill_to__too_long = (
    'The "address1_bill_to" parameter is invalid. "address1_bill_to" cannot be longer than 100 characters.'
)
address1_deliver_to__too_long = (
    'The "address1_deliver_to" parameter is invalid. "address1_deliver_to" cannot be longer than 100 characters.'
)
address2_bill_to__too_long = (
    'The "address2_bill_to" parameter is invalid. "address2_bill_to" cannot be longer than 100 characters.'
)
address2_deliver_to__too_long = (
    'The "address2_deliver_to" parameter is invalid. "address2_deliver_to" cannot be longer than 100 characters.'
)
address3_bill_to__too_long = (
    'The "address3_bill_to" parameter is invalid. "address3_bill_to" cannot be longer than 100 characters.'
)
address3_deliver_to__too_long = (
    'The "address3_deliver_to" parameter is invalid. "address3_deliver_to" cannot be longer than 100 characters.'
)
city_deliver_to__required_string = (
    'The "city_deliver_to" parameter is invalid. "city_deliver_to" is required and must be a string.'
)
city_bill_to__too_long = (
    'The "city_bill_to" parameter is invalid. "city_bill_to" cannot be longer than 50 characters.'
)
city_deliver_to__too_long = (
    'The "city_deliver_to" parameter is invalid. "city_deliver_to" cannot be longer than 50 characters.'
)
contra_address_id__required_int = (
    'The "contra_address_id" parameter is invalid. "contra_address_id" is required and must be an int.'
)
contra_address_id__invalid_id = (
    'The "contra_address_id" parameter is invalid. "contra_address_id" must belong to a valid Address that your '
    'Address is linked to.'
)
contra_contact__too_long = (
    'The "contra_contact" parameter is invalid. "contra_contact" cannot be longer than 100 characters.'
)
contra_contact_id__not_int = 'The "contra_contact_id" parameter is invalid. "contra_contact_id" must be an integer.'
contra_contact_id__invalid_id = (
    'The "contra_contact_id" parameter is invalid. "contra_contact_id" must belong to a valid User from the specified '
    'Contra Address.'
)
country_id_deliver_to__not_int = (
    'The "country_id_deliver_to" parameter is invalid. "country_id_deliver_to" must be an integer.'
)
country_id_deliver_to__required_int = (
    'The "country_id_deliver_to" parameter is invalid. "country_id_deliver_to" is required must be an integer.'
)
country_id_deliver_to__invalid_id = (
    'The "country_id_deliver_to" parameter is invalid. "country_id_deliver_to" must belong to a valid Country record.'
)
external_reference__too_long = (
    'The "external_reference" parameter is invalid. "external_reference" cannot be longer than 50 characters.'
)
lines__not_list = 'The "lines" parameter is invalid. "lines" is required and must be a list.'
lines__negative_total = (
    'The "lines" parameter is invalid. The gross amount on the transaction must not be a negative number.'
)
lines_description__too_long = (
    'The "lines" parameter is invalid. The "description" of each item in "lines" must be less than 250 characters long.'
)
lines_description__required_string = (
    'The "lines" parameter is invalid. Each item in "lines" must contain a "description".'
)
lines_exchange_rate__not_decimal = (
    'The "lines" parameter is invalid. The "exchange_rate" of a line must be a string in decimal format.'
)
lines_items__not_dict = (
    'The "lines" parameter is invalid. Each item in "lines" must be a dictionary.'
)
lines_number__invalid_account = (
    'The "lines" parameter is invalid. One of the items in "lines" uses a Nominal Account "number" that does not belong'
    ' to any Nominal Account in your Address.'
)
lines_number__required_purchases = (
    'The "lines" parameter is invalid. Each item in "lines" must contain a Nominal Account "number" referencing a '
    'Purchases Account in your Address.'
)
lines_number__required_sales = (
    'The "lines" parameter is invalid. Each item in "lines" must contain a Nominal Account "number" referencing a '
    'Sales Account in your Address.'
)
lines_number__out_of_range = (
    'The "lines" parameter is invalid. The "number" for a line must be within the range 0 to 7999 inclusive.'
)
lines_number__required_int = (
    'The "lines" parameter is invalid. Each item in "lines" must contain a Nominal Account "number" which must be an '
    'integer.'
)
lines_quantity__required_decimal = (
    'The "lines" parameter is invalid. Each item in "lines" must specify the "quantity" of items in the transaction. '
    'This "quantity" must be a string in decimal format'
)
lines_tax_amount__incorrectly_calculated = (
    'The "lines" parameter is invalid. The "tax_amount" specified in the line differs from the amount calculated using'
    ' the "tax_rate", "unit_price", and the "quantity". Please re-check the calculations. +/- 0.02 limit is allowed'
)
lines_tax_amount__not_decimal = (
    'The "lines" parameter is invalid. The "tax_amount" for a line must be a string in decimal format.'
)
lines_tax_rate__required_decimal = (
    'The "lines" parameter is invalid. Each item in "lines" must contain a "tax_rate" string in decimal format.'
)
lines_tax_rate_id__invalid_id = (
    'The "lines" parameter is invalid. One of the items in "lines" uses a "tax_rate_id" that does not belong to any '
    'Tax Rate record in your Address.'
)
lines_tax_rate_id__required_int = (
    'The "lines" parameter is invalid. Each item in "lines" must contain a "tax_rate_id" which must be an integer.'
)
lines_unit_price__required_decimal = (
    'The "lines" parameter is invalid. Each item in "lines" must contain a "unit_price" string in decimal format.'
)
name_deliver_to__required_string = (
    'The "name_deliver_to" parameter is invalid. "name_deliver_to" is required and must be a string.'
)
name_deliver_to__too_long = (
    'The "name_deliver_to" parameter is invalid. "name_deliver_to" cannot be longer than 250 characters.'
)
name_bill_to__too_long = (
    'The "name_bill_to" parameter is invalid. "name_bill_to" cannot be longer than 250 characters.'
)
narrative__too_long = 'The "narrative" parameter is invalid. "narrative" cannot be longer than 250 characters.'
payment_method_id__invalid_id = (
    'The "payment_method_id" parameter is invalid. "payment_method_id" must belong to a valid Payment Method record in'
    ' your Member.'
)
payment_method_id__no_address_account = (
    'The "payment_method_id" parameter is invalid. The Nominal Account specified by the Nominal Contra does not have '
    'an Address Nominal Account set up for your Address.'
)
payment_method_id__required_int = (
    'The "payment_method_id" parameter is invalid. "payment_method_id" is requried and must be an integer.'
)
postcode_bill_to__too_long = (
    'The "postcode_bill_to" parameter is invalid. "postcode_bill_to" cannot be longer than 20 characters.'
)
postcode_deliver_to__too_long = (
    'The "postcode_deliver_to" parameter is invalid. "postcode_deliver_to" cannot be longer than 20 characters.'
)
report_template_id__not_int = 'The "report_template_id" parameter is invalid. "report_template_id" must be an integer.'
report_template_id__invalid_id = (
    'The "report_template_id" parameter is invalid. "report_template_id" must belong to a valid Report Template record.'
)
subdivision_id_deliver_to__invalid_id = (
    'The "subdivision_id_deliver_to" parameter is invalid. "subdivision_id_deliver_to" must belong to a valid '
    'Subdivision record.'
)
subdivision_id_deliver_to__no_country_id = (
    'The "subdivision_id_deliver_to" parameter is invalid. You cannot specify a "subdivision_id_deliver_to" without '
    'specifying a "country_id_deliver_to".'
)
subdivision_id_deliver_to__not_int = (
    'The "subdivision_id_deliver_to" parameter is invalid. "subdivision_id_deliver_to" must be an integer.'
)
transaction_date__not_isoformat = (
    'The "transaction_date" parameter is invalid. "transaction_date" is required and must be a date string in '
    'isoformat.'
)
transaction_date__period_ended = (
    'The "transaction_date" parameter is invalid. This "transaction_date" has already been processed by a period end.'
)
tsn__required_int = 'The "tsn" parameter is invalid. "tsn" is required and must be an integer.'


# Permissions
not_self_managed = 'You do not have permission to make this request. Your Member must be self-managed'
