"""
Management for Balance Sheets
This service displays aggregated data from the Nominal Ledger. It does not create Balance Sheet records
"""

# stdlib
import copy
from decimal import Decimal
# libs
from cloudcix_rest.exceptions import Http400
from cloudcix_rest.views import APIView
from django.conf import settings
from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial import reserved_accounts as reserved
from financial.controllers.balance_sheet import BalanceSheetListController
from financial.models import GlobalNominalAccount, NominalLedgerCredit, NominalLedgerDebit
from financial.permissions.balance_sheet import Permissions
from financial.serializers import StatementSerializer
from financial.utils import AccountContainer, get_addresses_in_member


__all__ = [
    'BalanceSheetCollection',
]


class BalanceSheetCollection(APIView):
    """
    Handles methods regarding the Nominal Ledger that don't require an id to be specified
    """

    serializer_class = StatementSerializer

    def get(self, request: Request) -> Response:
        """
        summary: Calculate the balance in each of an Address' Balance Sheet Nominal Accounts on a certain date

        description: |
            Get the total debits and credits for all Nominal Accounts in an Address on a certain date where the Account
            Number is less than 4000. A global active User can generate a balance sheet for another Address in their
            Member by specifying an Address id. If a global active User does not specify an Address id, the balance
            sheet will be calculated using each Address in their Member.

        responses:
            200:
                description: A list of Nominal Accounts with the outstanding amount in each one
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = BalanceSheetListController(data=request.GET, request=request, span=span)
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
                'nominal_account_number__lt': 4000,
                'nominal_ledger__transaction_date__lte': cd['date'],
                'nominal_ledger__transaction_type_id__range': (10000, 12001),
            }

            if not request.user.global_active:
                filters['nominal_ledger__address_id'] = request.user.address['id']

            else:
                if cd['address_id'] is not None:
                    filters['nominal_ledger__address_id'] = cd['address_id']
                else:
                    # A global-active user has not specified an Address id. They should see a Balance sheet for their
                    # entire Member
                    filters['nominal_ledger__address_id__in'] = get_addresses_in_member(request, span)

        with tracer.start_span('get_objects', child_of=request.span) as span:
            with tracer.start_span('get_debits', child_of=span):
                # When gathering for the Debits/Credits, first apply the search filters. Then calculate the transaction
                # amounts in the Member's base currency (amount * exchange_rate). Group the transactions by
                # `nominal_account_number`, then sum up all the transaction amounts for each account number
                debits = NominalLedgerDebit.objects.filter(
                    **filters,
                ).values(
                    'nominal_account_number',
                ).annotate(
                    total=Coalesce(Sum('amount'), Decimal('0')),
                ).order_by(
                    'nominal_account_number',
                )

                # Store the data in Containers. Keep these in a dictionary for easy access
                objs = {
                    d['nominal_account_number']: AccountContainer(total_debits=d['total'].quantize(Decimal('1.0000')))
                    for d in debits
                }

            with tracer.start_span('get_credits', child_of=span):
                credits = NominalLedgerCredit.objects.filter(
                    **filters,
                ).values(
                    'nominal_account_number',
                ).annotate(
                    total=Coalesce(Sum('amount'), Decimal('0')),
                ).order_by(
                    'nominal_account_number',
                )

                # Aggregate the credit and debit data
                for c in credits:
                    c['total'] = c['total'].quantize(Decimal('1.0000'))
                    if c['nominal_account_number'] in objs:
                        objs[c['nominal_account_number']].total_credits = c['total']
                    else:
                        objs[c['nominal_account_number']] = AccountContainer(total_credits=c['total'])

        with tracer.start_span('get_accounts', child_of=request.span):
            accounts = GlobalNominalAccount.objects.filter(
                nominal_account_number__in=objs.keys(),
                member_id=request.user.member['id'],
            )

            # Set up a dummy account for any Accounts that could not be found. The dummy account should throw 404s if a
            # User tries to search for it
            try:
                dummy_account = copy.copy(accounts[0])
            except IndexError:  # pragma: no cover
                # This should only ever run if no accounts could be found for the transactions
                dummy_account = GlobalNominalAccount.objects.get(
                    member_id=request.user.member['id'],
                    nominal_account_number=reserved.CREDITOR_CONTROL_ACCOUNT,
                )
            dummy_account.id = 0
            dummy_account.description = 'NOT FOUND'
            dummy_account.valid_purchases_account = False
            dummy_account.valid_sales_account = False

            # Put the results in a dict for easier access
            accounts = {a.nominal_account_number: a for a in accounts}

        with tracer.start_span('generate_results', child_of=request.span):
            capital = current_assets = current_liabilities = fixed_assets = long_term_liabilities = Decimal('0')
            for account_number, obj in objs.items():
                # Match up the Nominal Accounts with their balances
                if account_number in accounts:
                    obj.nominal_account = accounts[account_number]
                else:
                    obj.nominal_account = copy.copy(dummy_account)
                    obj.nominal_account.nominal_account_number = account_number

                # Calculate the balance in each account. For debits calculate how much is owed to the Address, for
                # credits calculate how much is owed by the Address
                if account_number < 2300:
                    # Short term (current) assets and liabilities are calculated as normal, debits - credits
                    balance = obj.total_debits - obj.total_credits
                else:
                    # For longer term liabilities, the total is recorded as a credit, with repayments recorded as debits
                    # We want to find how much is still payable -> credits - debits
                    balance = obj.total_credits - obj.total_debits

                if account_number < 1000:
                    fixed_assets += balance
                elif account_number < 2000:
                    current_assets += balance
                elif account_number < 2300:
                    current_liabilities += balance
                elif account_number < 3000:
                    long_term_liabilities += balance
                else:
                    capital += balance

                obj.balance = balance

            total_assets = current_assets + fixed_assets
            total_liabilities = current_liabilities + long_term_liabilities
            total_retained = total_assets - total_liabilities - capital

        with tracer.start_span('gathering_metadata', child_of=request.span):
            metadata = {
                'capital': str(capital),
                'current_assets': str(current_assets),
                'current_liabilities': str(current_liabilities),
                'fixed_assets': str(fixed_assets),
                'long_term_liabilities': str(long_term_liabilities),
                'total_assets': str(total_assets),
                'total_liabilities': str(total_liabilities),
                'total_retained': str(total_retained),
            }

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            # objs is a dictionary of Account Numbers and Containers. Pass the Containers to be serialized
            span.set_tag('num_objects', len(objs))
            data = StatementSerializer(instance=objs.values(), many=True).data

        return Response({'content': data, '_metadata': metadata})
