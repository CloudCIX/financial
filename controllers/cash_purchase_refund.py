# stdlib
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from collections import deque
from typing import cast, Deque, Dict, List, Optional, Set, Union
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.controllers import ControllerBase
# local
from financial import reserved_accounts as reserved
from financial.controllers.transaction_mixin import FinancialException, TransactionMixin
from financial.models import (
    AddressNominalAccount,
    NominalLedger,
    NominalLedgerDebit,
    TaxRate,
)


__all__ = [
    'CashPurchaseRefundCreateController',
    'CashPurchaseRefundUpdateController',
]


CREDIT = Dict[str, Union[int, str, Decimal]]
DEBIT = CREDIT


class CashPurchaseRefundCreateController(ControllerBase, TransactionMixin):
    """
    Validate User data to create a new Nominal Ledger record for a Cash Sale Receipt transaction
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = NominalLedger
        validation_order = (
            'address1_bill_to',
            'address1_deliver_to',
            'address2_bill_to',
            'address2_deliver_to',
            'address3_bill_to',
            'address3_deliver_to',
            'city_bill_to',
            'city_deliver_to',
            'contra_contact',
            'country_id_deliver_to',
            'external_reference',
            'name_bill_to',
            'name_deliver_to',
            'narrative',
            'postcode_bill_to',
            'postcode_deliver_to',
            'subdivision_id_deliver_to',
            'transaction_date',
            'lines',
            'payment_method_id',
            'report_template_id',
        )

    def validate_address1_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The first line of the geographic address to bill the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            address = self._validate_address1_bill_to(address, 'financial_cash_purchase_refund_create_101')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address1_bill_to'] = address
        return None

    def validate_address1_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The first line of the geographic address to deliver the items of the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            address = self._validate_address1_deliver_to(address, 'financial_cash_purchase_refund_create_102')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address1_deliver_to'] = address
        return None

    def validate_address2_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The second line of the geographic address to bill the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            address = self._validate_address2_bill_to(address, 'financial_cash_purchase_refund_create_103')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address2_bill_to'] = address
        return None

    def validate_address2_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The second line of the geographic address to deliver the items on the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            address = self._validate_address2_deliver_to(address, 'financial_cash_purchase_refund_create_104')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address2_deliver_to'] = address
        return None

    def validate_address3_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The third line of the geographic address to bill the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            address = self._validate_address3_bill_to(address, 'financial_cash_purchase_refund_create_105')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address3_bill_to'] = address
        return None

    def validate_address3_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The third line of the geographic address to deliver the items on the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            address = self._validate_address3_deliver_to(address, 'financial_cash_purchase_refund_create_106')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address3_deliver_to'] = address
        return None

    def validate_city_bill_to(self, city: Optional[str]) -> Optional[str]:
        """
        description: The city where the company on the Cash Sale Receipt is situated
        type: string
        required: false
        """
        try:
            city = self._validate_city_bill_to(city, 'financial_cash_purchase_refund_create_107')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['city_bill_to'] = city
        return None

    def validate_city_deliver_to(self, city: Optional[str]) -> Optional[str]:
        """
        description: The city to deliver the items on the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            city = self._validate_city_deliver_to(city, 'financial_cash_purchase_refund_create_108')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['city_deliver_to'] = city
        return None

    def validate_contra_contact(self, contra_contact: Optional[str]) -> Optional[str]:
        """
        description: The name of the person who requested the Cash Purchase Refund
        type: string
        required: false
        """
        try:
            contra_contact = self._validate_contra_contact(contra_contact, 'financial_cash_purchase_refund_create_109')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['contra_contact'] = contra_contact
        return None

    def validate_country_id_deliver_to(self, country_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the country to deliver the items on the Cash Purchase Refund to
        type: integer
        required: false
        """
        try:
            country_id = self._validate_country_id(
                country_id,
                'financial_cash_purchase_refund_create_110',
                'financial_cash_purchase_refund_create_111',
            )
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['country_id_deliver_to'] = country_id
        return None

    def validate_external_reference(self, external_reference: Optional[str]) -> Optional[str]:
        """
        description: The identifier of this Cash Purchase Refund in the Contra Address's referencing scheme
        type: string
        required: false
        """
        try:
            external_reference = self._validate_external_reference(
                external_reference,
                'financial_cash_purchase_refund_create_112',
            )
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['external_reference'] = external_reference
        return None

    def validate_name_bill_to(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name of the company to bill the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            name = self._validate_name_bill_to(name, 'financial_cash_purchase_refund_create_113')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['name_bill_to'] = name
        return None

    def validate_name_deliver_to(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name of the company to deliver the items on the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            name = self._validate_name_deliver_to(name, 'financial_cash_purchase_refund_create_114')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['name_deliver_to'] = name
        return None

    def validate_narrative(self, narrative: Optional[str]) -> Optional[str]:
        """
        description: A summary of the Cash Purchase Refund and its items
        type: string
        required: false
        """
        try:
            narrative = self._validate_narrative(narrative, 'financial_cash_purchase_refund_create_115')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['narrative'] = narrative
        return None

    def validate_postcode_bill_to(self, postcode: Optional[str]) -> Optional[str]:
        """
        description: The postcode of the company to bill the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            postcode = self._validate_postcode_bill_to(postcode, 'financial_cash_purchase_refund_create_116')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['postcode_bill_to'] = postcode
        return None

    def validate_postcode_deliver_to(self, postcode: Optional[str]) -> Optional[str]:
        """
        description: The postcode of the company to deliver the items on the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            postcode = self._validate_postcode_deliver_to(postcode, 'financial_cash_purchase_refund_create_117')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['postcode_deliver_to'] = postcode
        return None

    def validate_subdivision_id_deliver_to(self, subdivision_id: Optional[int]) -> Optional[str]:
        """
        description: The subdivision of the company to deliver the items on the Cash Purchase Refund to
        type: integer
        required: false
        """
        try:
            subdivision_id = self._validate_subdivision_id(
                subdivision_id,
                'financial_cash_purchase_refund_create_118',
                'financial_cash_purchase_refund_create_119',
            )
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['subdivision_id_deliver_to'] = subdivision_id
        return None

    def validate_transaction_date(self, transaction_date: Optional[str]) -> Optional[str]:
        """
        description: The date that the Cash Purchase Refund was made
        type: string
        """
        try:
            transaction_date = self._validate_transaction_date(
                transaction_date,
                'financial_cash_purchase_refund_create_120',
                'financial_cash_purchase_refund_create_121',
            )
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['transaction_date'] = transaction_date
        return None

    def validate_lines(self, lines: Optional[List[CREDIT]]) -> Optional[str]:

        """
        description: A collection of the amounts to credit from each Nominal Account for this Cash Sale Receipt
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
            return 'financial_cash_purchase_refund_create_122'

        account_numbers: Set[int] = set()
        tax_rate_ids: Set[int] = set()
        for line in lines:
            if not isinstance(line, dict):
                return 'financial_cash_purchase_refund_create_123'

            try:
                description = cast(str, line['description'])
            except KeyError:
                return 'financial_cash_purchase_refund_create_124'
            if len(description) > NominalLedgerDebit._meta.get_field('description').max_length:
                return 'financial_cash_purchase_refund_create_125'

            try:
                line['exchange_rate'] = Decimal(str(line.get('exchange_rate', 1)))
            except InvalidOperation:
                return 'financial_cash_purchase_refund_create_126'

            try:
                number = int(cast(int, line['number']))
                if number not in range(0, 8000):
                    return 'financial_cash_purchase_refund_create_127'
                line['number'] = number
                account_numbers.add(number)
            except (KeyError, TypeError, ValueError):
                return 'financial_cash_purchase_refund_create_128'

            try:
                line['quantity'] = Decimal(str(line['quantity']))
            except (InvalidOperation, KeyError):
                return 'financial_cash_purchase_refund_create_129'

            if 'tax_amount' in line:
                try:
                    line['tax_amount'] = Decimal(str(line['tax_amount']))
                except InvalidOperation:
                    return 'financial_cash_purchase_refund_create_130'

            try:
                tax_rate_id = int(cast(int, line['tax_rate_id']))
                line['tax_rate_id'] = tax_rate_id
                tax_rate_ids.add(tax_rate_id)
            except (KeyError, TypeError, ValueError):
                return 'financial_cash_purchase_refund_create_131'

            try:
                line['unit_price'] = Decimal(str(line['unit_price']))
            except (InvalidOperation, KeyError):
                return 'financial_cash_purchase_refund_create_132'

        # Make sure all the Nominal Accounts exist
        accounts = AddressNominalAccount.objects.filter(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number__in=account_numbers,
        )
        if len(accounts) != len(account_numbers):
            return 'financial_cash_purchase_refund_create_133'
        for a in accounts:
            if not a.global_nominal_account.valid_purchases_account and \
                    a.global_nominal_account.nominal_account_number != reserved.VAT_CONTROL_ACCOUNT:
                return 'financial_cash_purchase_refund_create_134'

        # Make sure all the Tax Rates exist
        tax_rates = TaxRate.objects.filter(
            address_id=self.request.user.address['id'],
            id__in=tax_rate_ids,
        )
        if len(tax_rates) != len(tax_rate_ids):
            return 'financial_cash_purchase_refund_create_135'
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
                    return 'financial_cash_purchase_refund_create_136'
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
            return 'financial_cash_purchase_refund_create_137'

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
        self.cleaned_data['credits'] = results
        self.cleaned_data['debit'] = {
            'amount': (gross_amount + tax_amount).quantize(rounding_figure, rounding=ROUND_HALF_UP),
            'exchange_rate': 1,
            'quantity': 0,
            'unit_price': 0,
        }
        return None

    def validate_payment_method_id(self, payment_method_id: Optional[int]) -> Optional[str]:
        """
        description: How the company intends to accept the money for the Cash Purchase Refund
        type: integer
        """
        try:
            address_account = self._validate_payment_method_id(
                payment_method_id,
                10007,
                'financial_cash_purchase_refund_create_138',
                'financial_cash_purchase_refund_create_139',
                'financial_cash_purchase_refund_create_140',
                'financial_cash_purchase_refund_create_141',
                'financial_cash_purchase_refund_create_142',
            )
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address_account'] = address_account
        return None

    def validate_report_template_id(self, report_template_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Report Template to use when printing the Cash Purchase Refund
        type: integer
        """
        try:
            report_template_id = self._validate_report_template_id(
                report_template_id,
                10007,
                'financial_cash_purchase_refund_create_143',
                'financial_cash_purchase_refund_create_144',
                'financial_cash_purchase_refund_create_145',
            )
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['report_template_id'] = report_template_id
        return None


class CashPurchaseRefundUpdateController(ControllerBase, TransactionMixin):
    """
    Validate User data to create a new Nominal Ledger record for a Cash Purchase Refund transaction
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = NominalLedger
        validation_order = (
            'address1_bill_to',
            'address1_deliver_to',
            'address2_bill_to',
            'address2_deliver_to',
            'address3_bill_to',
            'address3_deliver_to',
            'city_bill_to',
            'city_deliver_to',
            'contra_contact',
            'country_id_deliver_to',
            'external_reference',
            'name_bill_to',
            'name_deliver_to',
            'narrative',
            'postcode_bill_to',
            'postcode_deliver_to',
            'subdivision_id_deliver_to',
        )

    def validate_address1_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The first line of the geographic address to bill the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            address = self._validate_address1_bill_to(address, 'financial_cash_purchase_refund_update_101')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address1_bill_to'] = address
        return None

    def validate_address1_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The first line of the geographic address to deliver the items on the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            address = self._validate_address1_deliver_to(address, 'financial_cash_purchase_refund_update_102')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address1_deliver_to'] = address
        return None

    def validate_address2_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The second line of the geographic address to bill the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            address = self._validate_address2_bill_to(address, 'financial_cash_purchase_refund_update_103')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address2_bill_to'] = address
        return None

    def validate_address2_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The second line of the geographic address to deliver the items on the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            address = self._validate_address2_deliver_to(address, 'financial_cash_purchase_refund_update_104')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address2_deliver_to'] = address
        return None

    def validate_address3_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The third line of the geographic address to bill the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            address = self._validate_address3_bill_to(address, 'financial_cash_purchase_refund_update_105')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address3_bill_to'] = address
        return None

    def validate_address3_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The third line of the geographic address to deliver the items on the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            address = self._validate_address3_deliver_to(address, 'financial_cash_purchase_refund_update_106')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address3_deliver_to'] = address
        return None

    def validate_city_bill_to(self, city: Optional[str]) -> Optional[str]:
        """
        description: The city where the company on the the Cash Purchase Refund is situated
        type: string
        required: false
        """
        try:
            city = self._validate_city_bill_to(city, 'financial_cash_purchase_refund_update_107')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['city_bill_to'] = city
        return None

    def validate_city_deliver_to(self, city: Optional[str]) -> Optional[str]:
        """
        description: The city to deliver the items on the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            city = self._validate_city_deliver_to(city, 'financial_cash_purchase_refund_update_108')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['city_deliver_to'] = city
        return None

    def validate_contra_contact(self, contra_contact: Optional[str]) -> Optional[str]:
        """
        description: The name of the person who requested the Cash Purchase Refund
        type: string
        required: false
        """
        try:
            contra_contact = self._validate_contra_contact(contra_contact, 'financial_cash_purchase_refund_update_109')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['contra_contact'] = contra_contact
        return None

    def validate_country_id_deliver_to(self, country_id: Optional[int]) -> Optional[str]:
        """
        description: The country to deliver the items on the Cash Purchase Refund
        type: integer
        required: false
        """
        try:
            country_id = self._validate_country_id(
                country_id,
                'financial_cash_purchase_refund_update_110',
                'financial_cash_purchase_refund_update_111',
            )
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['country_id_deliver_to'] = country_id
        return None

    def validate_external_reference(self, external_reference: Optional[str]) -> Optional[str]:
        """
        description: The identifier of this Cash Purchase Refund in the Contra Address's referencing scheme
        type: string
        required: false
        """
        try:
            external_reference = self._validate_external_reference(
                external_reference,
                'financial_cash_purchase_refund_update_112',
            )
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['external_reference'] = external_reference
        return None

    def validate_name_bill_to(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name of the company to bill the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            name = self._validate_name_bill_to(name, 'financial_cash_purchase_refund_update_113')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['name_bill_to'] = name
        return None

    def validate_name_deliver_to(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name of the company to deliver the items on the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            name = self._validate_name_deliver_to(name, 'financial_cash_purchase_refund_update_114')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['name_deliver_to'] = name
        return None

    def validate_narrative(self, narrative: Optional[str]) -> Optional[str]:
        """
        description: A summary of the Cash Purchase Refund and its items
        type: string
        required: false
        """
        try:
            narrative = self._validate_narrative(narrative, 'financial_cash_purchase_refund_update_115')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['narrative'] = narrative
        return None

    def validate_postcode_bill_to(self, postcode: Optional[str]) -> Optional[str]:
        """
        description: The postcode to bill the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            postcode = self._validate_postcode_bill_to(postcode, 'financial_cash_purchase_refund_update_116')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['postcode_bill_to'] = postcode
        return None

    def validate_postcode_deliver_to(self, postcode: Optional[str]) -> Optional[str]:
        """
        description: The postcode to deliver the items on the Cash Purchase Refund to
        type: string
        required: false
        """
        try:
            postcode = self._validate_postcode_deliver_to(postcode, 'financial_cash_purchase_refund_update_117')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['postcode_deliver_to'] = postcode
        return None

    def validate_subdivision_id_deliver_to(self, subdivision_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the subdivision to deliver the items on the Cash Purchase Refund to
        type: integer
        required: false
        """
        if subdivision_id is None:
            return None

        try:
            subdivision_id = int(cast(int, subdivision_id))
        except (TypeError, ValueError):
            return 'financial_cash_purchase_refund_update_118'

        if 'country_id_deliver_to' in self._errors:
            # Error validating country id
            return None
        else:
            country_id = self.cleaned_data.get('country_id_deliver_to', self._instance.country_id_deliver_to)
            if country_id is None:
                return 'financial_cash_purchase_refund_update_119'

        response = Membership.subdivision.read(
            token=self.request.user.token,
            pk=subdivision_id,
            country_id=country_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_cash_purchase_refund_update_120'

        self.cleaned_data['subdivision_id_deliver_to'] = subdivision_id
        return None
