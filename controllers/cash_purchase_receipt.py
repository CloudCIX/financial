# stdlib
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from collections import deque
from typing import cast, Deque, Dict, List, Optional, Set, Union
# libs
from cloudcix.api import Membership, Reporting
from cloudcix_rest.controllers import ControllerBase
# local
from financial import reserved_accounts as reserved
from financial.models import (
    AddressNominalAccount,
    NominalContra,
    NominalLedger,
    NominalLedgerDebit,
    PaymentMethod,
    TaxRate,
)


__all__ = [
    'CashPurchaseReceiptCreateController',
    'CashPurchaseReceiptUpdateController',
]

DEBIT = Dict[str, Union[int, str, Decimal]]
VALID_ACCOUNT_RANGE = range(1000, 3000)


class CashPurchaseReceiptCreateController(ControllerBase):

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = NominalLedger
        validation_order = (
            'address1_bill_to',
            'address2_bill_to',
            'address3_bill_to',
            'city_bill_to',
            'name_bill_to',
            'postcode_bill_to',
            'address1_deliver_to',
            'address2_deliver_to',
            'address3_deliver_to',
            'city_deliver_to',
            'country_id_deliver_to',
            'name_deliver_to',
            'postcode_deliver_to',
            'subdivision_id_deliver_to',
            'external_reference',
            'lines',
            'narrative',
            'payment_method_id',
            'report_template_id',
            'transaction_date',
            'contra_contact',
        )

    def validate_address1_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The first line of the geographic address to bill the Cash Purchase Receipt to
        type: string
        """
        if address is None:
            address = ''
        if len(address) > self.get_field('address1_bill_to').max_length:
            return 'financial_cash_purchase_receipt_create_101'
        self.cleaned_data['address1_bill_to'] = address
        return None

    def validate_address2_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The second line of the geographic address to bill the Cash Purchase Receipt to
        type: string
        """
        if address is None:
            address = ''
        if len(address) > self.get_field('address2_bill_to').max_length:
            return 'financial_cash_purchase_receipt_create_102'
        self.cleaned_data['address2_bill_to'] = address
        return None

    def validate_address3_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The third line of the geographic address to bill the Cash Purchase Receipt to
        type: string
        """
        if address is None:
            address = ''
        if len(address) > self.get_field('address3_bill_to').max_length:
            return 'financial_cash_purchase_receipt_create_103'
        self.cleaned_data['address3_bill_to'] = address
        return None

    def validate_city_bill_to(self, city_bill_to: Optional[str]) -> Optional[str]:
        """
        description: The city of the geographic address to bill the Cash Purchase Receipt to
        type: string
        """
        if city_bill_to is None:
            city_bill_to = ''
        if len(city_bill_to) > self.get_field('city_bill_to').max_length:
            return 'financial_cash_purchase_receipt_create_104'
        self.cleaned_data['city_bill_to'] = city_bill_to
        return None

    def validate_name_bill_to(self, name_bill_to: Optional[str]) -> Optional[str]:
        """
        description: The city of the geographic address to bill the Cash Purchase Receipt to
        type: string
        """
        if name_bill_to is None:
            name_bill_to = ''
        if len(name_bill_to) > self.get_field('name_bill_to').max_length:
            return 'financial_cash_purchase_receipt_create_105'
        self.cleaned_data['name_bill_to'] = name_bill_to
        return None

    def validate_postcode_bill_to(self, postcode_bill_to: Optional[str]) -> Optional[str]:
        """
        description: The postcode that the Purchase Receipt's items will be delivered to
        type: string
        required: false
        """
        if postcode_bill_to is None:
            postcode_bill_to = ''
        postcode_bill_to = str(postcode_bill_to).strip()
        if len(postcode_bill_to) > self.get_field('postcode_bill_to').max_length:
            return 'financial_cash_purchase_receipt_create_106'
        self.cleaned_data['postcode_bill_to'] = postcode_bill_to
        return None

    def validate_address1_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The first line of the geographic address to deliver the items of the Cash Purchase Receipt to
        type: string
        """
        if address is None:
            address = ''
        if len(address) > self.get_field('address1_deliver_to').max_length:
            return 'financial_cash_purchase_receipt_create_107'
        self.cleaned_data['address1_deliver_to'] = address
        return None

    def validate_address2_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The second line of the geographic address to deliver the items of the Cash Purchase Receipt to
        type: string
        required: false
        """
        if address is None:
            address = ''
        address = str(address).strip()
        if len(address) > self.get_field('address2_deliver_to').max_length:
            return 'financial_cash_purchase_receipt_create_108'
        self.cleaned_data['address2_deliver_to'] = address
        return None

    def validate_address3_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The third line of the geographic address to deliver the items of the Cash Purchase Receipt to
        type: string
        required: false
        """
        if address is None:
            address = ''
        address = str(address).strip()
        if len(address) > self.get_field('address3_deliver_to').max_length:
            return 'financial_cash_purchase_receipt_create_109'
        self.cleaned_data['address3_deliver_to'] = address
        return None

    def validate_city_deliver_to(self, city_deliver_to: Optional[str]) -> Optional[str]:
        """
        description: The city where the Cash Purchase Receipt's items will be delivered to
        type: string
        """
        if city_deliver_to is None:
            city_deliver_to = ''
        city_deliver_to = str(city_deliver_to).strip()
        if len(city_deliver_to) > self.get_field('city_deliver_to').max_length:
            return 'financial_cash_purchase_receipt_create_110'
        self.cleaned_data['city_deliver_to'] = city_deliver_to
        return None

    def validate_country_id_deliver_to(self, country_id_deliver_to: Optional[int]) -> Optional[str]:
        """
        description: The id of the Country where the Cash Purchase Receipt's items will be delivered to
        type: integer
        """
        if country_id_deliver_to is None:
            return None

        try:
            country_id_deliver_to = int(cast(int, country_id_deliver_to))
        except (TypeError, ValueError):
            return 'financial_cash_purchase_receipt_create_111'

        response = Membership.country.read(
            token=self.request.user.token,
            pk=country_id_deliver_to,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_cash_purchase_receipt_create_112'
        self.cleaned_data['country_id_deliver_to'] = country_id_deliver_to
        return None

    def validate_name_deliver_to(self, name_deliver_to: Optional[str]) -> Optional[str]:
        """
        description: The name of the company to deliver the Cash Purchase Receipt's items to
        type: string
        """
        if name_deliver_to is None:
            name_deliver_to = ''
        if len(name_deliver_to) > self.get_field('name_deliver_to').max_length:
            return 'financial_cash_purchase_receipt_create_113'
        self.cleaned_data['name_deliver_to'] = name_deliver_to
        return None

    def validate_postcode_deliver_to(self, postcode_deliver_to: Optional[str]) -> Optional[str]:
        """
        description: The postcode that the Purchase Receipt's items will be delivered to
        type: string
        required: false
        """
        if postcode_deliver_to is None:
            postcode_deliver_to = ''
        postcode_deliver_to = str(postcode_deliver_to).strip()
        if len(postcode_deliver_to) > self.get_field('postcode_deliver_to').max_length:
            return 'financial_cash_purchase_receipt_create_114'
        self.cleaned_data['postcode_deliver_to'] = postcode_deliver_to
        return None

    def validate_subdivision_id_deliver_to(self, subdivision_id_deliver_to: Optional[int]) -> Optional[str]:
        """
        description: The id of the Subdivision where the Purchase Receipt's items will be delivered to
        type: integer
        required: false
        """
        if subdivision_id_deliver_to is None:
            return None
        try:
            subdivision_id_deliver_to = int(cast(int, subdivision_id_deliver_to))
        except (TypeError, ValueError):
            return 'financial_cash_purchase_receipt_create_115'

        # A subdivision is only valid if a country is also specified
        if 'country_id_deliver_to' not in self.cleaned_data:
            if 'country_id_deliver_to' in self.errors:
                # Error validating the country id
                return None
            else:
                # Tried to use a subdivision without a country id
                return 'financial_cash_purchase_receipt_create_116'

        response = Membership.subdivision.read(
            token=self.request.user.token,
            pk=subdivision_id_deliver_to,
            country_id=self.cleaned_data['country_id_deliver_to'],
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_cash_purchase_receipt_create_117'
        self.cleaned_data['subdivision_id_deliver_to'] = subdivision_id_deliver_to
        return None

    def validate_external_reference(self, external_reference: Optional[str]) -> Optional[str]:
        """
        description: The identifier for this Cash Purchase Receipt in the Contra Address' referencing scheme
        type: string
        required: false
        """
        if external_reference is None:
            external_reference = ''
        external_reference = str(external_reference).strip()
        if len(external_reference) > self.get_field('external_reference').max_length:
            return 'financial_cash_purchase_receipt_create_118'
        self.cleaned_data['external_reference'] = external_reference
        return None

    def validate_lines(self, lines: Optional[List[DEBIT]]) -> Optional[str]:
        """
        description: A collection of the amounts to debit to each Nominal Account for this Cash Purchase Receipt
        type: array
        items:
            type: object
            properties:
                description:
                    type: string
                exchange_rate:
                    type: string
                    format: decimal
                number:
                    type: integer
                part_number:
                    type: integer
                quantity:
                    type: string
                    format: decimal
                tax_amount:
                    type: string
                    format: decimal
                tax_rate_id:
                    type: integer
                unit_price:
                    type: string
                    format: decimal
        """

        if not isinstance(lines, list):
            return 'financial_cash_purchase_receipt_create_119'

        account_numbers: Set[int] = set()
        tax_rate_ids: Set[int] = set()
        for line in lines:
            if not isinstance(line, dict):
                return 'financial_cash_purchase_receipt_create_120'

            try:
                description = cast(str, line['description'])
            except KeyError:
                return 'financial_cash_purchase_receipt_create_121'
            if len(description) > NominalLedgerDebit._meta.get_field('description').max_length:
                return 'financial_cash_purchase_receipt_create_122'

            try:
                line['exchange_rate'] = Decimal(str(line.get('exchange_rate', 1)))
            except InvalidOperation:
                return 'financial_cash_purchase_receipt_create_123'

            try:
                number = int(cast(int, line['number']))
                if number not in range(0, 8000):
                    return 'financial_cash_purchase_receipt_create_124'
                line['number'] = number
                account_numbers.add(number)
            except (KeyError, TypeError, ValueError):
                return 'financial_cash_purchase_receipt_create_125'

            try:
                line['quantity'] = Decimal(str(line['quantity']))
            except (InvalidOperation, KeyError):
                return 'financial_cash_purchase_receipt_create_126'

            if 'tax_amount' in line:
                try:
                    line['tax_amount'] = Decimal(str(line['tax_amount']))
                except InvalidOperation:
                    return 'financial_cash_purchase_receipt_create_127'
            try:
                tax_rate_id = int(cast(int, line['tax_rate_id']))
                line['tax_rate_id'] = tax_rate_id
                tax_rate_ids.add(tax_rate_id)
            except (KeyError, TypeError, ValueError):
                return 'financial_cash_purchase_receipt_create_128'

            try:
                line['unit_price'] = Decimal(str(line['unit_price']))
            except (InvalidOperation, KeyError):
                return 'financial_cash_purchase_receipt_create_129'

        # Make sure all the Nominal Accounts exist
        accounts = AddressNominalAccount.objects.filter(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number__in=account_numbers,
        )
        if len(accounts) != len(account_numbers):
            return 'financial_cash_purchase_receipt_create_130'
        for a in accounts:
            if not a.global_nominal_account.valid_purchases_account and \
                    a.global_nominal_account.nominal_account_number != reserved.VAT_CONTROL_ACCOUNT:
                return 'financial_cash_purchase_receipt_create_131'

        # Make sure all the Tax Rates exist
        tax_rates = TaxRate.objects.filter(
            address_id=self.request.user.address['id'],
            id__in=tax_rate_ids,
        )
        if len(tax_rates) != len(tax_rate_ids):
            return 'financial_cash_purchase_receipt_create_132'
        # Put the Tax Rate records in a dictionary for easy access
        tax_rates = {obj.id: obj for obj in tax_rates}

        # Now that the data is valid, calculate the transaction and tax amounts
        gross_amount = Decimal('0')
        tax_amount = Decimal('0')
        tax_error = Decimal('0.02')
        rounding_figure = Decimal('1.00')
        results: Deque[DEBIT] = deque()

        for line in lines:
            # Calculate the transaction subtotals
            unit_price = cast(Decimal, line['unit_price'])
            quantity = cast(Decimal, line['quantity'])

            # Calculate the amount of the line
            amount = (unit_price * quantity).quantize(rounding_figure, rounding=ROUND_HALF_UP)

            # Calculate amounts and tax in the User's base currency
            exchange_rate = cast(Decimal, line['exchange_rate'])
            gross_amount += amount * exchange_rate

            # Validate the tax on each item
            tax_rate = tax_rates[line['tax_rate_id']]
            tax_percent = cast(Decimal, tax_rate.percent)
            partial_tax = amount * tax_percent / 100

            if 'tax_amount' in line:
                if (partial_tax - tax_error) <= cast(Decimal, line['tax_amount']) <= (partial_tax + tax_error):
                    tax_amount += cast(Decimal, line['tax_amount']) * exchange_rate
                else:
                    return 'financial_cash_purchase_receipt_create_133'
            else:
                # The User didn't send a tax amount so use what we calculated
                tax_amount += partial_tax * exchange_rate

            results.append({
                'amount': amount,
                'description': line['description'],
                'exchange_rate': exchange_rate,
                'nominal_account_number': line['number'],
                'part_number': line.get('part_number', ''),
                'quantity': quantity,
                'tax_percent': tax_percent,
                'tax_rate': tax_rate,
                'unit_price': unit_price,
            })

        if gross_amount <= Decimal('0'):
            return 'financial_cash_purchase_receipt_create_134'

        # Now go and get the description of the VAT Control Account
        vat_description = AddressNominalAccount.objects.values_list(
            'description',
            flat=True,
        ).get(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number=reserved.VAT_CONTROL_ACCOUNT,
        )

        # Add an entry for total VAT
        results.append({
            'amount': (tax_amount).quantize(rounding_figure, rounding=ROUND_HALF_UP),
            'description': vat_description,
            'exchange_rate': 1,
            'nominal_account_number': reserved.VAT_CONTROL_ACCOUNT,
            'quantity': 0,
            'unit_price': 0,
        })
        self.cleaned_data['debits'] = results
        self.cleaned_data['credit'] = {
            'amount': (gross_amount + tax_amount).quantize(rounding_figure, rounding=ROUND_HALF_UP),
            'exchange_rate': 1,
            'quantity': 0,
            'unit_price': 0,
        }
        return None

    def validate_narrative(self, narrative: Optional[str]) -> Optional[str]:
        """
        description: A summary of the Purchase Receipt and its items
        type: string
        required: false
        """
        if narrative is None:
            narrative = ''
        narrative = str(narrative).strip()
        if len(narrative) > self.get_field('narrative').max_length:
            return 'financial_cash_purchase_receipt_create_135'
        self.cleaned_data['narrative'] = narrative
        return None

    def validate_payment_method_id(self, payment_method_id: Optional[int]) -> Optional[str]:
        """
        description: |
            How the requesting User intends to pay the Receipt. This will determine what Account will be credited by
            checking the Nominal Contra records
        type: integer
        """
        try:
            payment_method_id = int(cast(int, payment_method_id))
        except (TypeError, ValueError):
            return 'financial_cash_purchase_receipt_create_136'

        try:
            PaymentMethod.objects.get(
                id=payment_method_id,
                member_id=self.request.user.member['id'],
            )
        except PaymentMethod.DoesNotExist:
            return 'financial_cash_purchase_receipt_create_137'

        # Find out which Nominal Account will be credited by checking the Nominal Contras
        try:
            nominal_account_id = NominalContra.objects.values_list('global_nominal_account_id').get(
                payment_method_id=payment_method_id,
                transaction_type_id=10006,
            )
        except NominalContra.DoesNotExist:
            return 'financial_cash_purchase_receipt_create_138'

        # Make sure the Nominal Account pointed to by the Nominal Contra has an Address Nominal Account set up for the
        # User's Address
        try:
            address_account = AddressNominalAccount.objects.get(
                address_id=self.request.user.address['id'],
                global_nominal_account_id=nominal_account_id,
            )
        except AddressNominalAccount.DoesNotExist:
            return 'financial_cash_purchase_receipt_create_139'

        if address_account.global_nominal_account.nominal_account_number not in VALID_ACCOUNT_RANGE:
            return 'financial_cash_purchase_receipt_create_140'

        self.cleaned_data['address_account'] = address_account
        return None

    def validate_report_template_id(self, report_template_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Report Template to use when printing the Cash Purchase Receipt
        type: integer
        """
        if report_template_id is None:
            return None
        try:
            report_template_id = int(cast(int, report_template_id))
        except (TypeError, ValueError):
            return 'financial_cash_purchase_receipt_create_141'
        response = Reporting.report_template.read(
            token=self.request.user.token,
            pk=report_template_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_cash_purchase_receipt_create_142'
        if response.json()['content']['idTransactionType'] != 10006:
            return 'financial_cash_purchase_receipt_create_143'
        self.cleaned_data['report_template_id'] = report_template_id
        return None

    def validate_transaction_date(self, date: Optional[str]) -> Optional[str]:
        """
        description: The date that the Purchase Receipt was issued
        type: string
        """
        try:
            transaction_date = datetime.strptime(str(date).split('T')[0], '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return 'financial_cash_purchase_receipt_create_144'
        obj = NominalLedger.period_end.filter(
            address_id=self.request.user.address['id'],
            transaction_date__gte=transaction_date,
        )
        if obj.exists():
            return 'financial_cash_purchase_receipt_create_145'
        self.cleaned_data['transaction_date'] = transaction_date
        return None

    def validate_contra_contact(self, contra_contact: Optional[str]) -> Optional[str]:
        """
        description: The name of the person who sold the items on the Cash Purchase Receipt
        type: string
        """
        if contra_contact is None:
            contra_contact = ''
        if len(contra_contact) > self.get_field('contra_contact').max_length:
            return 'financial_cash_purchase_receipt_create_146'
        self.cleaned_data['contra_contact'] = contra_contact
        return None


class CashPurchaseReceiptUpdateController(ControllerBase):
    """
    Validate User data to update an existing Nominal Ledger record for a Cash Purchase Receipt transaction
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = NominalLedger
        validation_order = (
            'address1_bill_to',
            'address2_bill_to',
            'address3_bill_to',
            'city_bill_to',
            'name_bill_to',
            'postcode_bill_to',
            'address1_deliver_to',
            'address2_deliver_to',
            'address3_deliver_to',
            'city_deliver_to',
            'name_deliver_to',
            'country_id_deliver_to',
            'postcode_deliver_to',
            'subdivision_id_deliver_to',
            'external_reference',
            'contra_contact',
            'narrative',
        )

    def validate_address1_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The first line of the geographic address to bill the Cash Purchase Receipt to
        type: string
        """
        if address is None:
            address = ''
        if len(address) > self.get_field('address1_bill_to').max_length:
            return 'financial_cash_purchase_receipt_update_101'
        self.cleaned_data['address1_bill_to'] = address
        return None

    def validate_address2_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The second line of the geographic address to bill the Cash Purchase Receipt to
        type: string
        """
        if address is None:
            address = ''
        if len(address) > self.get_field('address2_bill_to').max_length:
            return 'financial_cash_purchase_receipt_update_102'
        self.cleaned_data['address2_bill_to'] = address
        return None

    def validate_address3_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The third line of the geographic address to bill the Cash Purchase Receipt to
        type: string
        """
        if address is None:
            address = ''
        if len(address) > self.get_field('address3_bill_to').max_length:
            return 'financial_cash_purchase_receipt_update_103'
        self.cleaned_data['address3_bill_to'] = address
        return None

    def validate_city_bill_to(self, city_bill_to: Optional[str]) -> Optional[str]:
        """
        description: The city of the geographic address to bill the Cash Purchase Receipt to
        type: string
        """
        if city_bill_to is None:
            city_bill_to = ''
        if len(city_bill_to) > self.get_field('city_bill_to').max_length:
            return 'financial_cash_purchase_receipt_update_104'
        self.cleaned_data['city_bill_to'] = city_bill_to
        return None

    def validate_name_bill_to(self, name_bill_to: Optional[str]) -> Optional[str]:
        """
        description: The city of the geographic address to bill the Cash Purchase Receipt to
        type: string
        """
        if name_bill_to is None:
            name_bill_to = ''
        if len(name_bill_to) > self.get_field('name_bill_to').max_length:
            return 'financial_cash_purchase_receipt_update_105'
        self.cleaned_data['name_bill_to'] = name_bill_to
        return None

    def validate_postcode_bill_to(self, postcode_bill_to: Optional[str]) -> Optional[str]:
        """
        description: The postcode that the Purchase Receipt's items will be delivered to
        type: string
        required: false
        """
        if postcode_bill_to is None:
            postcode_bill_to = ''
        postcode_bill_to = str(postcode_bill_to).strip()
        if len(postcode_bill_to) > self.get_field('postcode_bill_to').max_length:
            return 'financial_cash_purchase_receipt_update_106'
        self.cleaned_data['postcode_bill_to'] = postcode_bill_to
        return None

    def validate_address1_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The first line of the geographic address to deliver the items of the Cash Purchase Receipt to
        type: string
        """
        if address is None:
            address = ''
        if len(address) > self.get_field('address1_deliver_to').max_length:
            return 'financial_cash_purchase_receipt_update_107'
        self.cleaned_data['address1_deliver_to'] = address
        return None

    def validate_address2_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The second line of the geographic address to deliver the items of the Cash Purchase Receipt to
        type: string
        required: false
        """
        if address is None:
            address = ''
        address = str(address).strip()
        if len(address) > self.get_field('address2_deliver_to').max_length:
            return 'financial_cash_purchase_receipt_update_108'
        self.cleaned_data['address2_deliver_to'] = address
        return None

    def validate_address3_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The third line of the geographic address to deliver the items of the Cash Purchase Receipt to
        type: string
        required: false
        """
        if address is None:
            address = ''
        address = str(address).strip()
        if len(address) > self.get_field('address3_deliver_to').max_length:
            return 'financial_cash_purchase_receipt_update_109'
        self.cleaned_data['address3_deliver_to'] = address
        return None

    def validate_city_deliver_to(self, city_deliver_to: Optional[str]) -> Optional[str]:
        """
        description: The city where the Cash Purchase Receipt's items will be delivered to
        type: string
        """
        if city_deliver_to is None:
            city_deliver_to = ''
        city_deliver_to = str(city_deliver_to).strip()
        if len(city_deliver_to) > self.get_field('city_deliver_to').max_length:
            return 'financial_cash_purchase_receipt_update_110'
        self.cleaned_data['city_deliver_to'] = city_deliver_to
        return None

    def validate_country_id_deliver_to(self, country_id_deliver_to: Optional[int]) -> Optional[str]:
        """
        description: The id of the Country where the Cash Purchase Receipt's items will be delivered to
        type: integer
        """
        if country_id_deliver_to is None:
            return None

        try:
            country_id_deliver_to = int(cast(int, country_id_deliver_to))
        except (TypeError, ValueError):
            return 'financial_cash_purchase_receipt_update_111'

        response = Membership.country.read(
            token=self.request.user.token,
            pk=country_id_deliver_to,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_cash_purchase_receipt_update_112'
        self.cleaned_data['country_id_deliver_to'] = country_id_deliver_to
        return None

    def validate_name_deliver_to(self, name_deliver_to: Optional[str]) -> Optional[str]:
        """
        description: The name of the company to deliver the Cash Purchase Receipt's items to
        type: string
        """
        if name_deliver_to is None:
            name_deliver_to = ''
        if len(name_deliver_to) > self.get_field('name_deliver_to').max_length:
            return 'financial_cash_purchase_receipt_update_113'
        self.cleaned_data['name_deliver_to'] = name_deliver_to
        return None

    def validate_postcode_deliver_to(self, postcode_deliver_to: Optional[str]) -> Optional[str]:
        """
        description: The postcode that the Purchase Receipt's items will be delivered to
        type: string
        required: false
        """
        if postcode_deliver_to is None:
            postcode_deliver_to = ''
        postcode_deliver_to = str(postcode_deliver_to).strip()
        if len(postcode_deliver_to) > self.get_field('postcode_deliver_to').max_length:
            return 'financial_cash_purchase_receipt_update_114'
        self.cleaned_data['postcode_deliver_to'] = postcode_deliver_to
        return None

    def validate_subdivision_id_deliver_to(self, subdivision_id_deliver_to: Optional[int]) -> Optional[str]:
        """
        description: The id of the Subdivision where the Purchase Receipt's items will be delivered to
        type: integer
        required: false
        """
        if subdivision_id_deliver_to is None:
            return None
        try:
            subdivision_id_deliver_to = int(cast(int, subdivision_id_deliver_to))
        except (TypeError, ValueError):
            return 'financial_cash_purchase_receipt_update_115'

        # A subdivision is only valid if a country is also specified
        if 'country_id_deliver_to' in self.errors:
            # Error validating the country id
            return None
        else:
            country_id = self.cleaned_data.get('country_id_deliver_to', self._instance.country_id_deliver_to)
            if country_id is None:
                # Tried to use a subdivision without a country id
                return 'financial_cash_purchase_receipt_update_116'

        response = Membership.subdivision.read(
            token=self.request.user.token,
            pk=subdivision_id_deliver_to,
            country_id=country_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_cash_purchase_receipt_update_117'
        self.cleaned_data['subdivision_id_deliver_to'] = subdivision_id_deliver_to
        return None

    def validate_contra_contact(self, contra_contact: Optional[str]) -> Optional[str]:
        """
        description: The name of the person who sold the items on the Cash Purchase Receipt
        type: string
        """
        if contra_contact is None:
            contra_contact = ''
        if len(contra_contact) > self.get_field('contra_contact').max_length:
            return 'financial_cash_purchase_receipt_update_118'
        self.cleaned_data['contra_contact'] = contra_contact
        return None

    def validate_external_reference(self, external_reference: Optional[str]) -> Optional[str]:
        """
        description: The identifier for this Cash Purchase Receipt in the Contra Address' referencing scheme
        type: string
        required: false
        """
        if external_reference is None:
            return None
        external_reference = str(external_reference).strip()
        if len(external_reference) > self.get_field('external_reference').max_length:
            return 'financial_cash_purchase_receipt_update_119'
        self.cleaned_data['external_reference'] = external_reference
        return None

    def validate_narrative(self, narrative: Optional[str]) -> Optional[str]:
        """
        description: A summary of the Cash Purchase Receipt and its items
        type: string
        required: false
        """
        if narrative is None:
            narrative = ''
        narrative = str(narrative).strip()
        if len(narrative) > self.get_field('narrative').max_length:
            return 'financial_cash_purchase_receipt_update_120'
        self.cleaned_data['narrative'] = narrative
        return None
