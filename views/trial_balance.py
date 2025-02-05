"""
Management for Trial Balance
This service displays aggregated data from the Nominal Ledger. It does not create Trial Balance records
"""

# stdlib
import copy
from decimal import Decimal
# libs
from cloudcix_rest.exceptions import Http400
from django.conf import settings
from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial import reserved_accounts as reserved
from financial.api_view import FinancialAPIView as APIView
from financial.controllers.trial_balance import TrialBalanceListController
from financial.models import GlobalNominalAccount, NominalLedgerCredit, NominalLedgerDebit
from financial.permissions.trial_balance import Permissions
from financial.serializers.statement import StatementSerializer
from financial.utils import AccountContainer, get_addresses_in_member


__all__ = [
    'TrialBalanceCollection',
]


class TrialBalanceCollection(APIView):
    """
    Handles methods regarding Nominal Ledger records that don't require an id to be specified
    """

    serializer_class = StatementSerializer

    def get(self, request: Request) -> Response:
        """
        summary: Calculate the balance in each of an Address' Nominal Accounts up to a given date

        description: |
            Calculate the outstanding balance in an Address' Nominal Accounts up to a given date. A global active User
            can generate a Trial Balance statement for another Address in their Member by specifying an Address id. If
            a global active User does not specify an Address id, the Trial Balance statement will be calculated using
            each Address in their Member

        responses:
            200:
                description: A list of Nominal Accounts with the amount outstanding in each one
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = TrialBalanceListController(data=request.GET, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            cd = controller.cleaned_data
            err = Permissions.list(request, cd['address_id'], span)
            if err is not None:
                return err

        with tracer.start_span('set_search_filters', child_of=request.span):
            filters = {'nominal_ledger__transaction_date__lte': cd['date']}

            if not request.user.global_active:
                filters['nominal_ledger__address_id'] = request.user.address['id']

            else:
                if cd['address_id'] is not None:
                    filters['nominal_ledger__address_id'] = cd['address_id']
                else:
                    # A global-active User has not specified an Address id. They should see a Trial Balance for their
                    # entire Member
                    filters['nominal_ledger__address_id__in'] = get_addresses_in_member(request, span)

        with tracer.start_span('get_objects', child_of=request.span) as span:
            with tracer.start_span('get_debits', child_of=span):
                debits = NominalLedgerDebit.objects.filter(
                    **filters,
                ).exclude(
                    nominal_ledger__transaction_type_id=12001,
                ).values(
                    'nominal_account_number',
                ).annotate(
                    total=Coalesce(Sum('amount'), Decimal('0')),
                ).order_by(
                    'nominal_account_number',
                )

                # Store the Nominal Ledger data in Containers. Keep these in a dictionary for easy access
                objs = {
                    d['nominal_account_number']: AccountContainer(total_debits=d['total'].quantize(Decimal('1.0000')))
                    for d in debits if d['total'] != Decimal('0')
                }

            with tracer.start_span('get_credits', child_of=request.span):
                credits = NominalLedgerCredit.objects.filter(
                    **filters,
                ).exclude(
                    nominal_ledger__transaction_type_id=12001,
                ).values(
                    'nominal_account_number',
                ).annotate(
                    total=Coalesce(Sum('amount'), Decimal('0')),
                ).order_by(
                    'nominal_account_number',
                )

                # Aggregate the credit and debit data
                for c in credits:
                    total = c['total'].quantize(Decimal('1.0000'))

                    if c['nominal_account_number'] in objs:
                        objs[c['nominal_account_number']].total_credits = total
                    else:
                        objs[c['nominal_account_number']] = AccountContainer(total_credits=total)

        with tracer.start_span('filter_results', child_of=request.span):
            total_debits = total_credits = Decimal('0')
            for account_number, obj in objs.items():
                if obj.total_credits > obj.total_debits:
                    obj.total_credits -= obj.total_debits
                    obj.total_debits = Decimal('0.0000')
                    total_credits += obj.total_credits

                elif obj.total_credits < obj.total_debits:
                    obj.total_debits -= obj.total_credits
                    obj.total_credits = Decimal('0.0000')
                    total_debits += obj.total_debits

                else:
                    # The debits and credits equal. This Nominal Account doesn't need to appear in the Trial Balance
                    objs[account_number] = None

            # Filter out any items where the value has been set to None
            objs = {k: v for k, v in objs.items() if v is not None}

        with tracer.start_span('get_accounts', child_of=request.span):
            accounts = GlobalNominalAccount.objects.filter(
                nominal_account_number__in=objs.keys(),
                member_id=request.user.member['id'],
            )

            # Set up a dummy account for any Accounts that could not be found
            try:
                dummy_account = copy.copy(accounts[0])
            except IndexError:
                dummy_account = GlobalNominalAccount.objects.get(
                    member_id=request.user.member['id'],
                    nominal_account_number=reserved.CREDITOR_CONTROL_ACCOUNT,
                )
            dummy_account.id = 0
            dummy_account.description = 'NOT FOUND'
            dummy_account.valid_sales_account = False
            dummy_account.valid_purchases_account = False

            # Put the results in a dict for easier access
            accounts = {a.nominal_account_number: a for a in accounts}

            for account_number, obj in objs.items():
                if account_number in accounts:
                    obj.nominal_account = accounts[account_number]
                else:
                    obj.nominal_account = copy.copy(dummy_account)
                    obj.nominal_account.nominal_account_number = account_number

        with tracer.start_span('gathering_metadata', child_of=request.span):
            metadata = {
                'total_debits': str(total_debits),
                'total_credits': str(total_credits),
            }

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', len(objs))
            data = StatementSerializer(instance=objs.values(), many=True).data

        return Response({'content': data, '_metadata': metadata})
