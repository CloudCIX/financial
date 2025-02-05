"""
Management for Year End records
"""

# stdlib
from collections import deque
from decimal import Decimal
from typing import Deque
# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.db.models import Sum
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial import reserved_accounts as reserved
from financial.controllers.year_end import (
    YearEndCreateController,
    YearEndListController,
)
from financial.models import (
    NominalAccountHistory,
    NominalLedger,
    NominalLedgerCredit,
    NominalLedgerDebit,
)
from financial.permissions.year_end import Permissions
from financial.serializers.year_end import YearEndSerializer


__all__ = [
    'YearEndCollection',
    'YearEndResource',
]


class YearEndCollection(APIView):
    """
    Handles methods regarding Year End transactions that don't require an id to be specified i.e. list, create
    """

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of Year End transactions

        description: Retrieve a list of Nominal Ledger entries where the Transaction Type is for Year Ends

        responses:
            200:
                description: A list of Year End transactions, filtered and ordered by the User
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = YearEndListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the search filters
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span):
            order = controller.cleaned_data['order']
            try:
                objs = NominalLedger.year_ends.filter(
                    address_id=request.user.address['id'],
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    order,
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_year_end_list_001')

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
            }

        with tracer.start_span('serializing_data', child_of=request.span):
            span.set_tag('num_objects', objs.count())
            data = YearEndSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a Year End transaction

        description: |
            Create an entry on the Nominal Ledger where the Transaction Type is for Year Ends using data supplied by
            the User

        responses:
            200:
                description: Year End was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER
        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = YearEndCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('updating_controller', child_of=request.span):
            cd = controller.cleaned_data
            cd.update({
                'address_id': request.user.address['id'],
                'contra_address_id': request.user.address['id'],
                'unallocated_balance': Decimal('0'),
                'transaction_type_id': 12002,
            })

            # Check for a period end associated with this Year End
            period_end = NominalLedger.period_end.filter(
                address_id=cd['address_id'],
                transaction_date=cd['transaction_date'],
            )
            if not period_end.exists():
                NominalLedger.period_end.create(
                    address_id=cd['address_id'],
                    contra_address_id=cd['contra_address_id'],
                    narrative=cd['narrative'],
                    period_end_balance=cd['period_end_balance'],
                    transaction_date=cd['transaction_date'],
                )

        with tracer.start_span('closing_accounts', child_of=request.span):
            # To close the Accounts, we need to debit or credit each one so that all the debits and credits in the
            # Account sum to zero. First, find out how much is in each of the Trading Accounts (Account Number >= 4000)
            previous_year_end = cd.pop('previous_year_end')
            accounts = NominalAccountHistory.objects.filter(
                address_id=request.user.address['id'],
                transaction_date__gt=previous_year_end,
                transaction_date__lte=cd['transaction_date'],
                nominal_account_number__gte=4000,
            ).values(
                'nominal_account_number',
            ).annotate(
                balance=Sum('amount'),
            ).exclude(
                balance=Decimal('0'),
            )

            # Set up the debits or credits that will bring the outstanding balance in each Account to zero
            credits: Deque = deque()
            debits: Deque = deque()
            profit_loss = Decimal('0')
            for account in accounts:
                account_number = account['nominal_account_number']
                profit_loss += account['balance']

                if account['balance'] < 0:
                    # We need to debit this account to bring the amount to zero
                    debits.append({
                        'amount': account['balance'] * -1,
                        'nominal_account_number': account_number,
                    })
                elif account['balance'] > 0:
                    # We need to credit this account to bring the amount to zero
                    credits.append({
                        'amount': account['balance'],
                        'nominal_account_number': account_number,
                    })

            # Move the funds to the Profit and Loss Account
            if profit_loss < 0:
                credits.append({
                    'amount': profit_loss * -1,
                    'nominal_account_number': reserved.PROFIT_AND_LOSS_ACCOUNT,
                })
            elif profit_loss > 0:
                debits.append({
                    'amount': profit_loss,
                    'nominal_account_number': reserved.PROFIT_AND_LOSS_ACCOUNT,
                })

        with tracer.start_span('saving_objects', child_of=request.span) as span:
            with tracer.start_span('saving_ledger_entry', child_of=span):
                controller.instance.save()

            with tracer.start_span('saving_credits', child_of=span):
                NominalLedgerCredit.objects.bulk_create(
                    NominalLedgerCredit(
                        nominal_ledger_id=controller.instance.id,
                        **credit,
                    )
                    for credit in credits
                )

            with tracer.start_span('saving_debits', child_of=span):
                NominalLedgerDebit.objects.bulk_create(
                    NominalLedgerDebit(
                        nominal_ledger_id=controller.instance.id,
                        **debit,
                    )
                    for debit in debits
                )

        with tracer.start_span('serializing_data', child_of=request.span):
            data = YearEndSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class YearEndResource(APIView):
    """
    Handles methods regarding Year End transactions that require an id to be specified, i.e. read, update
    """

    def get(self, request: Request, tsn: int) -> Response:
        """
        summary: Read a Year End transaction with the specified tsn

        description: |
            Attempt to read a Nominal Ledger entry by the given tsn where the Transaction Type is for Year Ends,
            returning a 404 if it does not exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Year End to read
                type: integer

        responses:
            200:
                description: The Year End record was read successfully
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieve_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.year_ends.get(
                    address_id=request.user.address['id'],
                    tsn=tsn,
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_year_end_read_001')

        with tracer.start_span('serializing_data', child_of=request.span):
            data = YearEndSerializer(instance=obj).data

        return Response({'content': data})

    def delete(self, request: Request, tsn: int) -> Response:
        """
        summary: Delete a Year End record

        description: |
            Attempt to delete a Nominal Ledger entry by the given tsn where the Transaction Type is for Year Ends,
            returning a 404 if it does not exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Year End to delete
                type: integer

        responses:
            200:
                description: The Year End record was deleted successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieve_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.year_ends.get(
                    address_id=request.user.address['id'],
                    tsn=tsn,
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_year_end_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request, obj)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            obj.set_deleted()

        return Response(status=status.HTTP_204_NO_CONTENT)
