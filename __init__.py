"""
CloudCIX Financial is an Accounting API that allows Users to set up Nominal Accounts and conduct financial transactions
with other Addresses set up in CloudCIX Membership.

In order to conduct business using Financial a User must first set up their Nominal Accounts. Nominal Accounts are
divided into Global and Address Accounts. Global Accounts exists at the Member level and can be viewed by any Address
within the Member. Address Accounts are exist at the Address level and are linked to one of the Global Accounts.
Transactions can only be made onto the Address Accounts. This allows for each Address to maintain their own set of
Accounts while following the Account structure of their Member. The first time a User begins using the API a set of
Nominal Accounts are set up that are required by the service.

Financial transactions must be made between two CloudCIX Addresses. If another Address creates a transaction with your
own Address, the Financial API contains a service to make a contra transaction. That is, it will link the two
transactions, signifying that the transaction has been accepted.

There are services in the API that return aggregated data from the Nominal Accounts, such as VAT 3 reports, Profit and
Loss statements, Return of Trading Details, etc.

The API also contains a service for setting up automated Statements. By creating Statement Settings for your Address,
you are instructing the Financial API to send out a Statement of Account to each of your Debtors on a specified day of
each month. You can also set a minimum debit and credit value on these settings so that a Statement is only sent out to
Addresses whose outstanding balance is exceeds one of these minimum values.
"""

__version__ = '4.0.1'
