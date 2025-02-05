# stdlib
import copy
from decimal import Decimal
from typing import Dict, List
# libs
from cloudcix.api.membership import Membership
from django.db.models import Model, Q, Sum
from django.db.models.functions import Coalesce
from rest_framework.request import Request
# local
from financial.eu_countries import eu_countries
from financial.models import NominalLedgerCredit, NominalLedgerDebit


UK_LEFT_EU = '2020-12-31'


__all__ = [
    'AccountContainer',
    'get_addresses_in_member',
    'VIESCalculator',
    'VIESContainer',
]


class AccountContainer:
    """
    Make a structure to store data required for Financial Statements. Statements include Balance Sheets, Profit and Loss
    Account, and Trial Balance
    """
    __slots__ = 'balance', 'nominal_account', 'total_credits', 'total_debits'

    def __init__(self, total_debits=Decimal('0.0000'), total_credits=Decimal('0.0000')):
        self.total_debits = total_debits
        self.total_credits = total_credits
        self.balance = Decimal('0')
        self.nominal_account = None


def get_addresses_in_member(request, span) -> List[int]:
    """
    Given a token, make requests to Membership to fetch all the Addresses in the Member that the token is from
    """
    params = {
        'page': 0,
        'limit': 100,
        'search[member_id]': request.user.member['id'],
    }
    response = Membership.address.list(
        token=request.user.token,
        params=params,
        span=span,
    )
    address_ids = [a['id'] for a in response.json()['content']]

    total_records = response.json()['_metadata']['total_records']
    total_pages = total_records // params['limit']
    while params['page'] < total_pages:  # pragma: no cover
        params['page'] += 1
        response = Membership.address.list(
            token=request.user.token,
            params=params,
            span=span,
        )
        address_ids.extend([a['id'] for a in response.json()['content']])

    return address_ids


class VIESCalculator:
    """
    A class for calculating the total amount paid or received from a User's Address to other Addresses in the EU
    """
    _model: Model
    _address_id: int
    _country_id: int
    _tax_rate_id: int
    _filters: Dict

    def __init__(self, request: Request, tax_rate_id: int):
        self._address_id = request.user.address['id']
        self._country_id = request.user.address['country_id']
        self._tax_rate_id = tax_rate_id
        self._filters = dict()

    def set_model(self, model: Model):
        if model not in (NominalLedgerCredit, NominalLedgerDebit):  # pragma: no cover
            raise TypeError(f'Valid `model` values are NominalLedgerCredit and NominalLedgerDebit, not {model}')
        self._model = model

    def update_filters(self, **kwargs):
        self._filters.update(kwargs)

    def get_transaction_totals(self):
        """
        A query to calculate the total amount of money, charged at zero percent VAT, that was exchanged
        between the requesting User's Address and Addresses in other EU countries
        """
        # Only get transactions from Addresses in other EU countries
        eu_copy = copy.copy(eu_countries)
        try:
            eu_copy.pop(self._country_id)
        except KeyError:  # pragma: no cover
            list()

        results = self._model.objects.exclude(
            nominal_account_number=2210,
        ).filter(
            tax_rate_id=self._tax_rate_id,
            nominal_ledger__address_id=self._address_id,
            nominal_ledger__country_id_bill_to__in=eu_copy.keys(),
            **self._filters,
        ).exclude(
            Q(nominal_ledger__transaction_date__gt=UK_LEFT_EU) & Q(nominal_ledger__country_id_bill_to=826),
        ).values(
            'nominal_ledger__contra_address_id',
        ).annotate(
            amount=Coalesce(Sum('amount'), Decimal('0')),
        )

        return [VIESContainer(
            result['nominal_ledger__contra_address_id'],
            result['amount'].quantize(Decimal('1.0000')),
        ) for result in results]


class VIESContainer:
    """
    Make a structure to store data required for VIES statements
    """
    __slots__ = ['address_id', 'amount', 'used']

    def __init__(self, address_id, amount):
        self.address_id = address_id
        self.amount = amount
        self.used = False
