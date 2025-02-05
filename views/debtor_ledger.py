"""
Management for Debtors on Nominal Ledger records
"""

# stdlib
from collections import defaultdict, deque
from datetime import date, timedelta
from decimal import Decimal
from itertools import chain
from operator import itemgetter
from typing import Deque, Dict
# libs
from cloudcix_rest.exceptions import Http400
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import DecimalField, Q, Sum
from django.db.models.functions import Coalesce
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial import reserved_accounts as reserved
from financial.controllers.debtor_ledger import (
    DebtorLedgerAgedListController,
    DebtorLedgerContraTransactionListController,
    DebtorLedgerListController,
    DebtorLedgerTransactionListController,
)
from financial.models.nominal_ledger import NominalLedger
from financial.serializers.nominal_ledger import NominalLedgerSerializer
from financial.serializers.contra_nominal_ledger import ContraNominalLedgerSerializer

ALLOWED_TRANSACTION_TYPES = (11000, 11007)


__all__ = [
    'DebtorLedgerCollection',
    'DebtorLedgerAgedCollection',
    'DebtorLedgerTransactionCollection',
    'DebtorLedgerContraTransactionCollection',
]


class DebtorLedgerCollection(APIView):
    """
    Handles methods regarding Debtors on the Nominal Ledger that don't require an id to be specified i.e. list
    """

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of the outstanding balances between the User and their Debtors

        description: |
            Retrieve a list of Debtors along with the outstanding balance between them and the requesting User's Address

        responses:
            200:
                description: A list of Debtor Addresses with the outstanding balance for each one
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = DebtorLedgerListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the filters
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span):
            # Get all the Nominal Ledger objects that have a debit or credit referencing the Debtor Control Account
            try:
                debits = NominalLedger.objects.filter(
                    address_id=request.user.address['id'],
                    transaction_type_id__range=(11002, 11005),
                    debits__nominal_account_number=reserved.DEBTOR_CONTROL_ACCOUNT,
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).values(
                    'contra_address_id',
                ).annotate(
                    balance=Coalesce(Sum('debits__amount'), 0, output_field=DecimalField()),
                ).exclude(
                    balance=Decimal('0'),
                )

                credits = NominalLedger.objects.filter(
                    address_id=request.user.address['id'],
                    transaction_type_id__range=(11002, 11005),
                    credits__nominal_account_number=reserved.DEBTOR_CONTROL_ACCOUNT,
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).values(
                    'contra_address_id',
                ).annotate(
                    balance=Coalesce(Sum('credits__amount') * -1, 0, output_field=DecimalField()),
                ).exclude(
                    balance=Decimal('0'),
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_debtor_ledger_list_001')

        with tracer.start_span('calculating_balances', child_of=request.span):
            # Sum the debits to the credits for each Address
            lines = chain(debits, credits)
            balances: Dict = defaultdict(Decimal)
            for line in lines:
                balances[line['contra_address_id']] += line['balance']

            results: Deque = deque()
            total_balance = zero = Decimal('0')
            for address_id, balance in balances.items():
                if balance == zero:
                    continue
                total_balance += balance
                results.append({
                    'address_id': address_id,
                    'balance': balance,
                })
            # Cast the results to a list for sorting
            objs = list(results)

        with tracer.start_span('ordering_objects', child_of=request.span):
            order = controller.cleaned_data['order']
            reverse = order.startswith('-')
            if reverse:
                order = order.lstrip('-')
            objs.sort(key=itemgetter(order), reverse=reverse)

            # Cast the balances to strings
            for obj in objs:
                obj['balance'] = str(obj['balance'])

        with tracer.start_span('gathering_metadata', child_of=request.span):
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            total_records = len(objs)

            # Handle pagination
            objs = objs[page * limit: (page + 1) * limit]
            metadata = {
                'page': page,
                'limit': limit,
                'order': order,
                'warnings': controller.warnings,
                'total_records': total_records,
                'balance': str(total_balance),
            }

        return Response({'content': objs, '_metadata': metadata})


class DebtorLedgerAgedCollection(APIView):
    """
    Handles methods regarding Debtors on the Nominal Ledger that don't require an id to be specified i.e. list
    """

    @staticmethod
    def _period_balance(address_id, contra_address_id):
        """
        Create a function to calculate the period balances between two addresses for a specific date range
        """
        kw = {'address_id': address_id}
        if hasattr(contra_address_id, '__iter__'):
            kw['contra_address_id__in'] = contra_address_id
        else:
            kw['contra_address_id'] = contra_address_id

        def func(start_date, end_date):
            balance = NominalLedger.objects.filter(
                transaction_date__range=(start_date, end_date),
                transaction_type_id__range=(11002, 11005),
                **kw,
            ).exclude(
                unallocated_balance=Decimal('0'),
            ).aggregate(
                Sum('unallocated_balance'),
            )['unallocated_balance__sum'] or Decimal('0')

            return balance.quantize(Decimal('1.0000'))
        return func

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of Debtors with a breakdown of the outstanding balance for each one

        description: |
            Retrieve a list of Debtors along with the outstanding balance between them and the requesting User's Address
            on a Monthly basis

        responses:
            200:
                description: |
                    A list of Debtor Addresses with the outstanding balance for each one broken into date ranges
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = DebtorLedgerAgedListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the filters
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span):
            contra_address_ids = NominalLedger.objects.filter(
                address_id=request.user.address['id'],
                transaction_type_id__range=(11002, 11005),
            ).exclude(
                unallocated_balance=Decimal('0'),
            ).values_list(
                'contra_address_id',
                flat=True,
            ).order_by(
                'contra_address_id',
            ).distinct(
                'contra_address_id',
            )

        with tracer.start_span('ordering_objects', child_of=request.span):
            # Ordering and pagination are done on fields that need to be calculated first. To minimise the amount of
            # work required, we'll first calculate the balances for the field that the results will be ordered by. Once
            # pagination is done, we'll calculate the rest
            if 'order' not in request.GET:
                # Set a default if no order was sent
                order = '-current_balance'
            else:
                order = controller.cleaned_data['order']

            reverse = order.startswith('-')
            if reverse:
                order = order.lstrip('-')

            # Set up the dates that the records will be sorted by
            today = date.today()
            one_day = timedelta(days=1)
            thirty_days = timedelta(days=30)
            day30 = today - thirty_days
            day60 = day30 - thirty_days
            day90 = day60 - thirty_days
            day120 = day90 - thirty_days
            older = date(year=1900, month=1, day=1)
            date_ranges = {
                'balance_30_day': (day30, today),
                'balance_60_day': (day60, day30 - one_day),
                'balance_90_day': (day90, day60 - one_day),
                'balance_120_day': (day120, day90 - one_day),
                'older_balance': (older, day120 - one_day),
                'current_balance': (older, today),
            }

            dates = date_ranges.pop(order)
            results: Deque = deque()
            for contra_address_id in contra_address_ids:
                period_balance = self._period_balance(request.user.address['id'], contra_address_id)
                results.append({
                    'address_id': contra_address_id,
                    order: period_balance(*dates),
                })

            # Now handle pagination
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            total_records = len(results)
            objs = list(results)
            objs.sort(key=itemgetter(order), reverse=reverse)
            objs = objs[page * limit: (page + 1) * limit]

        with tracer.start_span('calculating_period_balances', child_of=request.span):
            for obj in objs:
                period_balance = self._period_balance(request.user.address['id'], obj['address_id'])
                # Calculate the balances for the remaining date ranges
                for key, date_range in date_ranges.items():
                    obj[key] = period_balance(*date_range)

        with tracer.start_span('calculating_total_balances', child_of=request.span):
            if total_records < limit:
                # If there were fewer objects than the limit, then we have all the objects that would be returned by the
                # filter. Just add up the balances to get the totals
                balance_30_day = balance_60_day = balance_90_day = balance_120_day = older_balance = current_balance = \
                    Decimal('0')
                for obj in objs:
                    balance_30_day += obj['balance_30_day']
                    balance_60_day += obj['balance_60_day']
                    balance_90_day += obj['balance_90_day']
                    balance_120_day += obj['balance_120_day']
                    older_balance += obj['older_balance']
                    current_balance += obj['current_balance']
            else:
                # There were other results that were not included so calculate the totals with a query
                period_balance = self._period_balance(request.user.address['id'], contra_address_ids)
                balance_30_day = period_balance(day30, today)
                balance_60_day = period_balance(day60, day30)
                balance_90_day = period_balance(day90, day60)
                balance_120_day = period_balance(day120, day90)
                older_balance = period_balance(older, day120)
                current_balance = period_balance(older, today)

        with tracer.start_span('gathering_metadata', child_of=request.span):
            # Cast all the decimals to strings
            for obj in objs:
                obj['balance_30_day'] = str(obj['balance_30_day'])
                obj['balance_60_day'] = str(obj['balance_60_day'])
                obj['balance_90_day'] = str(obj['balance_90_day'])
                obj['balance_120_day'] = str(obj['balance_120_day'])
                obj['older_balance'] = str(obj['older_balance'])
                obj['current_balance'] = str(obj['current_balance'])

            metadata = {
                'page': page,
                'limit': limit,
                'order': order,
                'warnings': controller.warnings,
                'total_records': total_records,
                'balance_30_day': str(balance_30_day),
                'balance_60_day': str(balance_60_day),
                'balance_90_day': str(balance_90_day),
                'balance_120_day': str(balance_120_day),
                'older_balance': str(older_balance),
                'current_balance': str(current_balance),
            }

        return Response({'content': objs, '_metadata': metadata})


class DebtorLedgerTransactionCollection(APIView):
    """
    Handles methods regarding Sale Transactions on the Nominal Ledger that don't require an id to be specified i.e. list
    """

    serializer_class = NominalLedgerSerializer

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of Sale Transactions

        description: Retrieve a list of Sale Transactions from the Nominal Ledger, created by the User's Address

        responses:
            200:
                description: A list of Sale Transactions, filtered and ordered by the User
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = DebtorLedgerTransactionListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the filters
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span):
            order = controller.cleaned_data['order']
            order2 = '-id' if order.startswith('-') else 'id'
            try:
                objs = NominalLedger.objects.filter(
                    address_id=request.user.address['id'],
                    transaction_type_id__range=ALLOWED_TRANSACTION_TYPES,
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    order,
                    order2,
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_debtor_ledger_transaction_list_001')

        with tracer.start_span('calculating_balances', child_of=request.span):
            credit_adjustment = Q(transaction_type_id=11005) & \
                Q(credits__nominal_account_number=reserved.DEBTOR_CONTROL_ACCOUNT)

            total_credits = NominalLedger.objects.filter(
                Q(transaction_type_id__in=(11001, 11003, 11004, 11007)) | credit_adjustment,
                address_id=request.user.address['id'],
            ).aggregate(
                balance=Coalesce(Sum('credits__amount'), 0, output_field=DecimalField()),
            )['balance'].quantize(Decimal('1.0000'))

            debit_adjustment = Q(transaction_type_id=11005) & \
                Q(debits__nominal_account_number=reserved.DEBTOR_CONTROL_ACCOUNT)
            total_debits = NominalLedger.objects.filter(
                Q(transaction_type_id__in=(11000, 11002, 11006)) | debit_adjustment,
                address_id=request.user.address['id'],
            ).aggregate(
                balance=Coalesce(Sum('debits__amount'), 0, output_field=DecimalField()),
            )['balance'].quantize(Decimal('1.0000'))

        with tracer.start_span('gathering_metadata', child_of=request.span):
            total_records = objs.count()
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            # Handle pagination
            objs = objs[page * limit: (page + 1) * limit]
            metadata = {
                'page': page,
                'limit': limit,
                'order': order,
                'warnings': controller.warnings,
                'total_records': total_records,
                'total_credits': str(total_credits),
                'total_debits': str(total_debits),
            }

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', len(objs))
            data = NominalLedgerSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})


class DebtorLedgerContraTransactionCollection(APIView):
    """
    Handles methods regarding Sale Transactions from Debtors that don't require an id to be specified i.e. list
    """

    serializer_class = ContraNominalLedgerSerializer

    def get(self, request: Request):
        """
        summary: Retrieve a list of Sale Transactions made out to the requesting User's Address

        description: |
            Retrieve a list of Sale Transactions that have no Contra Transactions, and have been made out to the
            requesting User's Address

        responses:
            200:
                description: |
                    A list of Sale Transactions made out to the User's Address that have not yet been accepted
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = DebtorLedgerContraTransactionListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the search filters
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span):
            order = controller.cleaned_data['order']
            order2 = '-id' if order.startswith('-') else 'id'
            try:
                objs = NominalLedger.objects.filter(
                    contra_address_id=request.user.address['id'],
                    contra_nominal_ledger__isnull=True,
                    transaction_type_id__range=ALLOWED_TRANSACTION_TYPES,
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    order,
                    order2,
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_debtor_ledger_contra_transaction_list_001')

        with tracer.start_span('gathering_metadata', child_of=request.span):
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            total_records = objs.count()
            # Handle pagination
            objs = objs[page * limit: (page + 1) * limit]
            metadata = {
                'page': page,
                'limit': limit,
                'order': order,
                'warnings': controller.warnings,
                'total_records': total_records,
            }

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = ContraNominalLedgerSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})
