"""
Error Codes for all of the Methods in the Journal Entry service
"""

from . import default

# List
financial_journal_entry_list_001 = (
    'One or more of the sent search fields contains invalid values. Please check the sent parameters and ensure they '
    'match the required patterns.'
)

# Create
financial_journal_entry_create_101 = (
    'The "credits" parameter is invalid. "credits" is required and must be a list of "amount" and "number" values '
    'specifying how much to credit from Nominal Accounts in your Member.'
)
financial_journal_entry_create_102 = (
    'The "credits" parameter is invalid. Each item in "credits" must contain an "amount" value, which must be a string '
    'in decimal format.'
)
financial_journal_entry_create_103 = (
    'The "credits" parameter is invalid. Each item in "credits" must contain a non-zero "amount" value.'
)
financial_journal_entry_create_104 = (
    'The "credits" parameter is invalid. Each item in "credits" must contain a "number" corresponding to a Nominal '
    'Account in your Address.'
)
financial_journal_entry_create_105 = (
    'The "credits" parameter is invalid. Each item in "credits" must contain a unique Nominal Account "number".'
)
financial_journal_entry_create_106 = (
    'The "credits" parameter is invalid. One of the "credits" references the Debtor or Creditor Control Account.'
)
financial_journal_entry_create_107 = (
    'The "credits" parameter is invalid. One of the "credits" uses a Nominal Account "number" that does not belong to '
    'any Nominal Account in your Address.'
)
financial_journal_entry_create_108 = (
    'The "debits" parameter is invalid. "debits" is required and must be a list of "amount" and "number" values '
    'specifying how much to debits to Nominal Accounts in your Member.'
)
financial_journal_entry_create_109 = (
    'The "debits" parameter is invalid. Each item in "debits" must contain an "amount" value, which must be a string '
    'in decimal format.'
)
financial_journal_entry_create_110 = (
    'The "debits" parameter is invalid. Each item in "debits" must contain a non-zero "amount" value.'
)
financial_journal_entry_create_111 = (
    'The "debits" parameter is invalid. Each item in "debits" must contain a "number" corresponding to a Nominal '
    'Account in your Address.'
)
financial_journal_entry_create_112 = (
    'The "debits" parameter is invalid. Each item in "debits" must contain a unique Nominal Account "number".'
)
financial_journal_entry_create_113 = (
    'The "debits" parameter is invalid. One of the "debits" references the Debtor or Creditor Control Account.'
)
financial_journal_entry_create_114 = (
    'The "debits" parameter is invalid. One of the "debits" uses a Nominal Account "number" that does not belong to '
    'any Nominal Account in your Address.'
)
financial_journal_entry_create_115 = (
    'The "debits" and/or "credits" parameters are invalid. A Nominal Account "number" must be unique accross all items '
    'in "debits" and "credits".'
)
financial_journal_entry_create_116 = (
    'The "debits" and/or "credits" parameters are invalid. The total "amount" from the debits and credits must be '
    'equal.'
)
financial_journal_entry_create_117 = default.narrative__too_long
financial_journal_entry_create_118 = default.report_template_id__not_int
financial_journal_entry_create_119 = default.report_template_id__invalid_id
financial_journal_entry_create_120 = (
    'The "report_template_id" parameter is invalid. The Report Template must be for Journal Entries.'
)
financial_journal_entry_create_121 = default.transaction_date__not_isoformat
financial_journal_entry_create_122 = default.transaction_date__period_ended
financial_journal_entry_create_201 = default.not_self_managed

# Read
financial_journal_entry_read_001 = (
    'The "tsn" path parameter is invalid. "tsn" must be a valid Transaction Sequence Number for a Journal Entry in '
    'your Address.'
)

# Update
financial_journal_entry_update_001 = (
    'The "tsn" path parameter is invalid. "tsn" must be a valid Transaction Sequence Number for a Journal Entry in '
    'your Address.'
)
financial_journal_entry_update_101 = default.narrative__too_long
financial_journal_entry_update_102 = default.report_template_id__not_int
financial_journal_entry_update_103 = default.report_template_id__invalid_id
financial_journal_entry_update_104 = (
    'The "report_template_id" parameter is invalid. The Report Template must be for Journal Entries.'
)
financial_journal_entry_update_105 = default.transaction_date__not_isoformat
financial_journal_entry_update_106 = default.transaction_date__period_ended

financial_journal_entry_update_201 = (
    'You do not have permission to make this request. This Journal Entry has already been processed by a Period End '
    'and cannot be updated.'
)
