"""
Management for specific Creditors on the Nominal Ledger
"""

# stdlib
from datetime import datetime, timedelta
from decimal import Decimal
# libs
from cloudcix_rest.exceptions import Http400
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial import reserved_accounts as reserved
from financial.controllers.creditor_account import (
    CreditorAccountListController,
)
from financial.models import (
    NominalLedger,
    NominalLedgerCredit,
    NominalLedgerDebit,
)
from financial.serializers import (
    CreditorAccountHistorySerializer,
    CreditorAccountStatementSerializer,
)

__all__ = [
    'CreditorAccountHistoryCollection',
    'CreditorAccountStatementCollection',
]


class CreditorAccountHistoryCollection(APIView):
    """
    Handles methods regarding the Nominal Ledger that don't require an id to be specified i.e. list
    """

    def get(self, request: Request, id: int) -> Response:
        """
        summary: List all transactions made with a given Creditor

        description: Retrieve all Nominal Ledger transactions between the requesting User and the specified Creditor

        path_params:
            id:
                description: The id of an Address that the requesting User deals with
                type: integer

        controller: CreditorAccountListController

        responses:
            200:
                description: Nominal Ledger transactions were read successfully
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = CreditorAccountListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the filters
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span):
            order = controller.cleaned_data['order']
            order2 = '-id' if order.startswith('-') else 'id'
            try:
                objs = NominalLedger.objects.filter(
                    address_id=request.user.address['id'],
                    contra_address_id=id,
                    transaction_type_id__range=(10000, 10005),
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    order,
                    order2,
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_creditor_account_history_list_001')

        with tracer.start_span('gathering_total_debits', child_of=request.span):
            debits = NominalLedgerDebit.objects.filter(
                nominal_account_number=reserved.CREDITOR_CONTROL_ACCOUNT,
                nominal_ledger__address_id=request.user.address['id'],
                nominal_ledger__contra_address_id=id,
                nominal_ledger__transaction_type_id__in=(10003, 10004, 10005),
            ).aggregate(
                Sum('amount'),
            )
            total_debits = Decimal(str(debits['amount__sum'] or 0)).quantize(Decimal('1.0000'))

        with tracer.start_span('gathering_total_credits', child_of=request.span):
            credits = NominalLedgerCredit.objects.filter(
                nominal_account_number=reserved.CREDITOR_CONTROL_ACCOUNT,
                nominal_ledger__address_id=request.user.address['id'],
                nominal_ledger__contra_address_id=id,
                nominal_ledger__transaction_type_id__in=(10002, 10005),
            ).aggregate(
                Sum('amount'),
            )
            total_credits = Decimal(str(credits['amount__sum'] or 0)).quantize(Decimal('1.0000'))

        with tracer.start_span('gathering_metadata', child_of=request.span):
            total_records = objs.count()
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            warnings = controller.warnings
            # Handle pagination
            objs = objs[page * limit: (page + 1) * limit]
            # Generate response data
            metadata = {
                'page': page,
                'limit': limit,
                'order': order,
                'warnings': warnings,
                'total_records': total_records,
                'total_credits': str(total_credits),
                'total_debits': str(total_debits),
            }

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = CreditorAccountHistorySerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})


class CreditorAccountStatementCollection(APIView):
    """
    Handles methods regarding unallocated transactions on the Nominal Ledger that don't require an id to be specified
    i.e. list
    """

    def get(self, request: Request, id: int) -> Response:
        """
        summary: List all transactions with a given Creditor that have not been fully allocated

        description: |
            Retrieve all Nominal Ledger transactions between the requesting User and the specified Creditor that have
            not been fully allocated

        path_params:
            id:
                description: The id of an Address that the requesting User deals with
                type: integer

        controller: CreditorAccountListController

        responses:
            200:
                description: Unallocated Nominal Ledger transactions were read successfully
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = CreditorAccountListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the filters
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span):
            order = controller.cleaned_data['order']
            order2 = '-id' if order.startswith('-') else 'id'
            try:
                purchase_filter = Q(transaction_type_id__range=(10002, 10005)) & \
                    Q(address_id=request.user.address['id']) & \
                    Q(contra_address_id=id)

                objs = NominalLedger.objects.filter(
                    purchase_filter,
                    **controller.cleaned_data['search'],
                ).exclude(
                    unallocated_balance=Decimal('0'),
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    order,
                    order2,
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_creditor_account_statement_list_001')

        with tracer.start_span('calculating_running_balances', child_of=request.span):
            total_records = objs.count()
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            # Handle pagination
            objs = objs[page * limit: (page + 1) * limit]

            # For each transaction in the response calculate the unallocated balances of all transactions before it
            # This is a lot of db hits so a better solution is welcome
            zero = Decimal('0')
            for obj in objs:
                date_filter = Q(transaction_date__lt=obj.transaction_date) | \
                    Q(transaction_date=obj.transaction_date) & \
                    Q(id__lte=obj.id)

                obj.running_balance = NominalLedger.objects.filter(
                    purchase_filter,
                    date_filter,
                ).aggregate(
                    balance=Coalesce(Sum('unallocated_balance'), zero),
                )['balance']

        with tracer.start_span('calculating_period_balances', child_of=request.span):
            today = datetime.utcnow()
            thirty_days = timedelta(days=30)
            day30 = today - thirty_days
            day60 = day30 - thirty_days
            day90 = day60 - thirty_days
            balances = NominalLedger.objects.filter(
                purchase_filter,
            ).aggregate(
                day30=Coalesce(Sum(
                    'unallocated_balance',
                    filter=Q(transaction_date__gt=day30, transaction_date__lte=today),
                ), zero),
                day60=Coalesce(Sum(
                    'unallocated_balance',
                    filter=Q(transaction_date__gt=day60, transaction_date__lte=day30),
                ), zero),
                day90=Coalesce(Sum(
                    'unallocated_balance',
                    filter=Q(transaction_date__gt=day90, transaction_date__lte=day60),
                ), zero),
                older=Coalesce(Sum(
                    'unallocated_balance',
                    filter=Q(transaction_date__lte=day90),
                ), zero),
            )

            # Calculate the total and cast all the values to strings
            total = Decimal('0')
            for k, v in balances.items():
                total += v
                balances[k] = str(v.quantize(Decimal('1.0000')))
            balances['current'] = str(total.quantize(Decimal('1.0000')))

        with tracer.start_span('gathering_metadata', child_of=request.span):
            # Generate response data
            metadata = {
                'page': page,
                'limit': limit,
                'order': order,
                'warnings': controller.warnings,
                'total_records': total_records,
                'balance_30_day': balances['day30'],
                'balance_60_day': balances['day60'],
                'balance_90_day': balances['day90'],
                'older_balance': balances['older'],
                'current_balance': balances['current'],
            }

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = CreditorAccountStatementSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})
