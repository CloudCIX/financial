# stdlib
from datetime import datetime, date
from typing import Callable, cast, Dict, Optional
# libs
from cloudcix.api import Membership, Reporting
from opentracing.span import Span
from rest_framework.request import Request
# local
from financial.models import AddressNominalAccount, NominalContra, NominalLedger, PaymentMethod


VALID_ACCOUNT_RANGE = range(1000, 3000)


class FinancialException(Exception):
    pass


# TODO: The 'pragma: no cover' comments can be removed once this class is applied to other transactions that use the
#  extra features of the mixin. Report templates do not exist for receipts and refunds yet, so they will be ignored
#  from coverage for the time being
class TransactionMixin:
    """
    Class for validating common transaction data
    """
    request: Request
    span: Span
    cleaned_data: Dict
    get_field: Callable

    #############################################
    #             String Validation             #
    #############################################
    def _validate_string_field(
            self,
            string: Optional[str],
            field: str,
            length_error: str,
            required_error: Optional[str] = None,
    ) -> str:
        """
        Validate that the length of a string is less than the maximum set by the model
        """
        if string is None:
            string = ''

        if required_error is not None and len(string) == 0:  # pragma: no cover
            raise FinancialException(required_error)

        string = str(string).strip()
        if len(string) > self.get_field(field).max_length:
            raise FinancialException(length_error)
        return string

    def _validate_address1_bill_to(self, address: Optional[str], length_error: str) -> str:
        return self._validate_string_field(address, 'address1_bill_to', length_error)

    def _validate_address1_deliver_to(
            self,
            address: Optional[str],
            length_error: str,
            required_error: Optional[str] = None,
    ) -> str:
        return self._validate_string_field(address, 'address1_deliver_to', length_error, required_error)

    def _validate_address2_bill_to(self, address: Optional[str], length_error: str) -> str:
        return self._validate_string_field(address, 'address2_bill_to', length_error)

    def _validate_address2_deliver_to(self, address: Optional[str], length_error: str) -> str:
        return self._validate_string_field(address, 'address2_deliver_to', length_error)

    def _validate_address3_bill_to(self, address: Optional[str], length_error: str) -> str:
        return self._validate_string_field(address, 'address3_bill_to', length_error)

    def _validate_city_bill_to(self, city: Optional[str], length_error: str) -> str:
        return self._validate_string_field(city, 'city_bill_to', length_error)

    def _validate_address3_deliver_to(self, address: Optional[str], length_error: str) -> str:
        return self._validate_string_field(address, 'address3_deliver_to', length_error)

    def _validate_city_deliver_to(
            self,
            city: Optional[str],
            length_error: str,
            required_error: Optional[str] = None,
    ) -> str:
        return self._validate_string_field(city, 'city_deliver_to', length_error, required_error)

    def _validate_contra_contact(self, contact: Optional[str], length_error: str) -> str:
        return self._validate_string_field(contact, 'contra_contact', length_error)

    def _validate_external_reference(self, reference: Optional[str], length_error: str) -> str:
        return self._validate_string_field(reference, 'external_reference', length_error)

    def _validate_name_bill_to(self, name: Optional[str], length_error: str) -> str:
        return self._validate_string_field(name, 'name_bill_to', length_error)

    def _validate_name_deliver_to(
            self,
            name: Optional[str],
            length_error: str,
            required_error: Optional[str] = None,
    ) -> str:
        return self._validate_string_field(name, 'name_deliver_to', length_error, required_error)

    def _validate_narrative(self, narrative: Optional[str], length_error: str) -> str:
        return self._validate_string_field(narrative, 'narrative', length_error)

    def _validate_postcode_bill_to(self, postcode: Optional[str], length_error: str) -> str:
        return self._validate_string_field(postcode, 'postcode_bill_to', length_error)

    def _validate_postcode_deliver_to(self, postcode: Optional[str], length_error: str) -> str:
        return self._validate_string_field(postcode, 'postcode_deliver_to', length_error)

    #############################################
    #            Integer Validation             #
    #############################################

    def _validate_country_id(
            self,
            country_id: Optional[int],
            int_error: str,
            does_not_exist_error: str,
            required: bool = False,
    ) -> Optional[int]:
        """
        Check that a country id is an integer and it exists in the Membership application
        """
        if country_id is None and not required:
            return None

        try:
            country_id = int(cast(int, country_id))
        except (TypeError, ValueError):
            raise FinancialException(int_error)

        response = Membership.country.read(
            token=self.request.user.token,
            pk=country_id,
            span=self.span,
        )
        if response.status_code != 200:
            raise FinancialException(does_not_exist_error)
        return country_id

    def _validate_subdivision_id(
            self,
            subdivision_id: Optional[int],
            int_error: str,
            does_not_exist_error: str,
    ) -> Optional[int]:
        """
        Check that a subdivision id is an integer and it exists in the Membership application
        """
        if subdivision_id is None:
            return None

        try:
            subdivision_id = int(cast(int, subdivision_id))
        except (TypeError, ValueError):
            raise FinancialException(int_error)

        country_id = self.cleaned_data.get('country_id_deliver_to')
        if country_id is None:
            return None

        response = Membership.subdivision.read(
            token=self.request.user.token,
            pk=subdivision_id,
            country_id=country_id,
            span=self.span,
        )
        if response.status_code != 200:
            raise FinancialException(does_not_exist_error)

        return subdivision_id

    def _validate_payment_method_id(
            self,
            payment_method_id: Optional[int],
            transaction_type_id: int,
            int_error: str,
            payment_method_does_not_exist_error: str,
            nominal_contra_does_not_exist_error: str,
            address_account_does_not_exist_error: str,
            invalid_account_error: str,

    ) -> AddressNominalAccount:
        """
        Check that a Payment Method id is an integer and it exists in the Financial database
        Retrieve the Nominal Contra set up for the Payment method and transaction type pair
        Check that an Address Account exists for Nominal Account specified by the Nominal Contra
        """
        try:
            payment_method_id = int(cast(int, payment_method_id))
        except (TypeError, ValueError):
            raise FinancialException(int_error)

        try:
            PaymentMethod.objects.get(
                id=payment_method_id,
                member_id=self.request.user.member['id'],
            )
        except PaymentMethod.DoesNotExist:
            raise FinancialException(payment_method_does_not_exist_error)

        # Find out which Nominal Account will be credited by checking the Nominal Contras
        try:
            nominal_account_id = NominalContra.objects.values_list('global_nominal_account_id').get(
                payment_method_id=payment_method_id,
                transaction_type_id=transaction_type_id,
            )
        except NominalContra.DoesNotExist:
            raise FinancialException(nominal_contra_does_not_exist_error)

        # Make sure the Nominal Account pointed to by the Nominal Contra has an Address Nominal Account set up for the
        # User's Address
        try:
            address_account = AddressNominalAccount.objects.get(
                address_id=self.request.user.address['id'],
                global_nominal_account_id=nominal_account_id,
            )
        except AddressNominalAccount.DoesNotExist:
            raise FinancialException(address_account_does_not_exist_error)

        if address_account.global_nominal_account.nominal_account_number not in VALID_ACCOUNT_RANGE:
            raise FinancialException(invalid_account_error)

        return address_account

    def _validate_report_template_id(
            self,
            report_template_id: Optional[int],
            transaction_type_id: int,
            int_error: str,
            does_not_exist_error: str,
            wrong_transaction_type_error: str,
    ) -> Optional[int]:
        """
        Check that the Report Template id is an integer and it exists in the Reporting Application
        Check that the Report Template uses the specified transaction type
        """
        if report_template_id is None:
            return None

        try:
            report_template_id = int(cast(int, report_template_id))
        except (TypeError, ValueError):
            raise FinancialException(int_error)

        response = Reporting.report_template.read(
            token=self.request.user.token,
            pk=report_template_id,
            span=self.span,
        )
        if response.status_code != 200:
            raise FinancialException(does_not_exist_error)

        if response.json()['content']['idTransactionType'] != transaction_type_id:  # pragma: no cover
            raise FinancialException(wrong_transaction_type_error)

        return report_template_id   # pragma: no cover

    #############################################
    #              Date Validation              #
    #############################################

    def _validate_transaction_date(self, date: Optional[str], iso_error: str, period_end_error: str) -> date:
        try:
            transaction_date = datetime.strptime(str(date).split('T')[0], '%Y-%m-%d').date()
        except (TypeError, ValueError):
            raise FinancialException(iso_error)

        obj = NominalLedger.period_end.filter(
            address_id=self.request.user.address['id'],
            transaction_date__gte=transaction_date,
        )
        if obj.exists():
            raise FinancialException(period_end_error)
        return transaction_date
