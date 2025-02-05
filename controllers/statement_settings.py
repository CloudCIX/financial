# python
# stdlib
from decimal import Decimal, InvalidOperation
from typing import cast, List, Optional, Union
# libs
from cloudcix_rest.controllers import ControllerBase
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
# local
from financial.models.statement_settings import StatementSettings


__all__ = [
    'StatementSettingsListController',
    'StatementSettingsUpdateController',
]


class StatementSettingsListController(ControllerBase):
    """
    Validates User data to filter a list of Statement Settings records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'address_id',
            'id',
        )
        search_fields = {
            'address_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class StatementSettingsUpdateController(ControllerBase):

    class Meta:
        model = StatementSettings
        validation_order = (
            'day',
            'min_credit',
            'min_debit',
            'reply_to',
            'signature',
        )

    def validate_day(self, day: Optional[List[int]]) -> Optional[str]:
        """
        description: The dates in each month that the statement will be sent out on
        type: array
        items:
            type: integer
        """
        day = day or []
        if not isinstance(day, list):
            return 'financial_statement_settings_update_101'

        days: List[int] = []
        for date in day:
            try:
                date = int(cast(int, date))
            except (ValueError, TypeError):
                return 'financial_statement_settings_update_102'
            if date < 1 or date > 31:
                return 'financial_statement_settings_update_103'
            days.append(date)
        self.cleaned_data['day'] = days

        return None

    def validate_min_credit(self, min_credit: Optional[Union[Decimal, int, str]]) -> Optional[str]:
        """
        description: |
            The mnimum amount of the credit balance that an account should have for an automated statement to be posted.
        type: string
        """
        if not min_credit:
            return None
        try:
            # Convert min_credit amount to a Decimal, then round to 2 decimal places
            min_credit = Decimal(str(min_credit))
        except (KeyError, InvalidOperation):
            return 'financial_statement_settings_update_104'
        if min_credit > 0:
            return 'financial_statement_settings_update_105'

        self.cleaned_data['min_credit'] = min_credit

        return None

    def validate_min_debit(self, min_debit: Optional[Union[Decimal, int, str]]) -> Optional[str]:
        """
        description: |
            The mnimum amount of the debit balance that an account should have for an automated statement to be posted.
        type: string
        """
        if not min_debit:
            return None
        try:
            # Convert min_debit amount to a Decimal, then round to 2 decimal places
            min_debit = Decimal(str(min_debit))
        except (KeyError, InvalidOperation):
            return 'financial_statement_settings_update_106'
        if min_debit < 0:
            return 'financial_statement_settings_update_107'

        self.cleaned_data['min_debit'] = min_debit

        return None

    def validate_reply_to(self, reply_to: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing email addresses in the format of 'Name <email@address.com>' or 'email@address.com',
            separated by commas
        type: string
        """
        if not reply_to:
            return None
        split = reply_to.split(',')
        for email in split:
            try:
                if '<' in email and email.endswith('>'):
                    email = email[email.find('<') + 1:-1]
                validate_email(email)
            except ValidationError:
                return 'financial_statement_settings_update_108'

        self.cleaned_data['reply_to'] = ','.join(entry.strip() for entry in split)

        return None

    def validate_signature(self, signature: Optional[str]) -> Optional[str]:
        """
        description: |
            A string containing the signature to attach to the end of the email being sent with the automated statement.
        type: string
        """
        self.cleaned_data['signature'] = signature or ''

        return None
