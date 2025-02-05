"""
Management for Sales by Country
This service displays aggregated data from the Nominal Ledger. It does not create Sales by Country records
"""

# stdlib
from decimal import Decimal
from typing import Dict
# libs
from cloudcix_rest.exceptions import Http400
from cloudcix_rest.views import APIView
from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial import reserved_accounts as reserved
from financial.controllers.sales_by_country import SalesByCountryListController
from financial.models import NominalLedgerCredit, NominalLedgerDebit
from financial.permissions.sales_by_country import Permissions
from financial.serializers import TransactionsByCountrySerializer
from financial.utils import get_addresses_in_member


__all__ = [
    'SalesByCountryCollection',
]


CREDIT_TRANSACTIONS = [11000, 11002, 11005, 11006]
DEBIT_TRANSACTIONS = [11001, 11003, 11005, 11007]


class SalesByCountryCollection(APIView):
    """
    Handles methods regarding the Nominal Ledger that don't require an id to be specified
    """

    serializer_class = TransactionsByCountrySerializer

    def get(self, request: Request) -> Response:
        """
        summary: Returns a list of Countries with total amounts per Country earned in Sales in a period of time.

        description: |
            This method allows the User to get a list of Countries with the amounts earned in Sales during a
            period of time. Each Country will have a total amount excluding VAT, a total amount of VAT and a total
            amount including VAT.
        responses:
            200:
                description: A list of Countries with their total balance in Sales
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = SalesByCountryListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the search filters
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            cd = controller.cleaned_data
            err = Permissions.list(request, cd.get('address_id'), span)
            if err is not None:
                return err

        with tracer.start_span('set_search_filter', child_of=request.span) as span:
            filters = {
                'nominal_ledger__transaction_date__gte': cd['start_date'],
                'nominal_ledger__transaction_date__lte': cd['finish_date'],
            }

            if not request.user.global_active:
                filters['nominal_ledger__address_id'] = request.user.address['id']

            else:
                if cd['address_id'] is not None:
                    filters['nominal_ledger__address_id'] = cd['address_id']
                else:
                    # A global-active user has not specified an Address id. They should be able to list Sales by Country
                    # for their entire Member
                    filters['nominal_ledger__address_id__in'] = get_addresses_in_member(request, span)

        with tracer.start_span('get_objects', child_of=request.span) as span:
            # When gathering for the Debits/Credits, first apply the search filters.
            # Then calculate the transaction amounts in the Member's base currency (amount * exchange_rate).
            objs: Dict = dict()

            with tracer.start_span('get_credits', child_of=span):
                credits = NominalLedgerCredit.objects.filter(
                    **filters,
                    nominal_ledger__transaction_type_id__in=CREDIT_TRANSACTIONS,
                ).order_by(
                    'nominal_ledger__country_id_bill_to',
                )
                # Store the data in Containers.
                # Keep these in a dictionary for easy access grouped by country_id_bill_to.
                for c in credits:
                    base_currency_total = c.amount * c.exchange_rate
                    country_id = c.nominal_ledger.country_id_bill_to

                    if country_id not in objs:
                        objs[country_id] = {
                            'balance': 0,
                            'country_id': country_id,
                            'excluding_vat': 0,
                            'vat': 0,
                        }

                    if c.nominal_account_number == reserved.VAT_CONTROL_ACCOUNT:
                        key = 'vat'
                    else:
                        key = 'excluding_vat'
                    objs[country_id][key] += base_currency_total

            with tracer.start_span('get_debits', child_of=span):
                debits = NominalLedgerDebit.objects.filter(
                    **filters,
                    nominal_ledger__transaction_type_id__in=DEBIT_TRANSACTIONS,
                ).order_by(
                    'nominal_ledger__country_id_bill_to',
                )
                for d in debits:
                    base_currency_total = d.amount * d.exchange_rate * -1
                    country_id = d.nominal_ledger.country_id_bill_to

                    if country_id not in objs:
                        objs[country_id] = {
                            'balance': 0,
                            'country_id': country_id,
                            'excluding_vat': 0,
                            'vat': 0,
                        }

                    if d.nominal_account_number == reserved.VAT_CONTROL_ACCOUNT:
                        key = 'vat'
                    else:
                        key = 'excluding_vat'
                    objs[country_id][key] += base_currency_total

        with tracer.start_span('generate_results', child_of=request.span):
            total_excluding_vat = total_vat = Decimal('0')
            for country_id, obj in objs.items():
                obj['balance'] = obj['excluding_vat'] + obj['vat']

                total_excluding_vat += obj['excluding_vat']
                total_vat += obj['vat']

            total_balance = total_excluding_vat + total_vat

        with tracer.start_span('gathering_metadata', child_of=request.span):
            metadata = {
                'total_balance': total_balance,
                'total_excluding_vat': total_excluding_vat,
                'total_vat': total_vat,
            }

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            # objs is a dictionary of Country_ids and Containers. Pass the Containers to be serialized
            span.set_tag('num_objects', len(objs))
            data = TransactionsByCountrySerializer(instance=objs.values(), many=True).data
        return Response({'content': data, '_metadata': metadata})
