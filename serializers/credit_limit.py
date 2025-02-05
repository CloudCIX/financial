"""
Dummy Credit_Limit Serializer to generate the Credit Limit schema
"""
# libs
import serpy


class CreditLimitSerializer(serpy.Serializer):
    """
    address1:
        description: The first line of the geographic address of the Address
        type: string
    address2:
        description: The second line of the geographic address of the Address
        type: string
    address3:
        description: The third line of the geographic address of the Address
        type: string
    billing_address_id:
        description: The id of the Address that receives bills for the Address
        type: integer
    city:
        description: The city in which the Address is located
        type: string
    country:
        $ref: 'https://membership.api.cloudcix.com/documentation/#/components/schemas/Country'
    credit_limit:
        description: |
            The agreed credit limit for Financials given to this address
            If set, the credit owed by this address to the requesting address cannot exceed this amount.
        type: string
        format: decimal
    currency:
        $ref: 'https://membership.api.cloudcix.com/documentation/#/components/schemas/Currency'
    current_credit:
        description: The current amount of credit owed by this address to the requesting address
        type: string
        format: decimal
    email:
        description: The email address of the Address
        type: string
    full_address:
        description: The full geographical address of the Address
        type: string
    gln:
        description: The Global Location Number of the Address
        type: string
    id:
        description: The id of the Address
        type: integer
    language:
        $ref: 'https://membership.api.cloudcix.com/documentation/#/components/schemas/Language'
    linked:
        description: A flag stating whether the requesting User's Address is linked to this one
        type: boolean
    member:
        $ref: 'https://membership.api.cloudcix.com/documentation/#/components/schemas/Member'
    phones:
        description: An array of named phone numbers used by this Address
        type: array
        items:
            type: object
            properties:
                name:
                    type: string
                number:
                    type: string
    postcode:
        description: The postcode of the geographical address of the Address
        type: string
    subdivision:
        $ref: 'https://membership.api.cloudcix.com/documentation/#/components/schemas/Subdivision'
    name:
        description: The name of the Address
        type: string
    vat_number:
        description: The vat number of the Address
        type: string
    website:
        description: The website of the Address
        type: string
    """
    address1 = serpy.Field()
    address2 = serpy.Field()
    address3 = serpy.Field()
    billing_address_id = serpy.Field()
    city = serpy.Field()
    country = serpy.Field()
    credit_limit = serpy.Field()
    currency = serpy.Field()
    current_credit = serpy.Field()
    email = serpy.Field()
    full_address = serpy.Field()
    gln = serpy.Field()
    id = serpy.Field()
    language = serpy.Field()
    linked = serpy.Field()
    member = serpy.Field()
    name = serpy.Field()
    phones = serpy.Field()
    postcode = serpy.Field()
    subdivision = serpy.Field()
    vat_number = serpy.Field()
    website = serpy.Field()
