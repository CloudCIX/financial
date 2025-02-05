"""
Management for transactions involving a specific Nominal Account
"""

# stdlib
from collections import deque
from decimal import Decimal
from typing import Deque
# libs
from cloudcix_rest.views import APIView
from cloudcix_rest.exceptions import Http400, Http404
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.controllers.nominal_account_history import NominalAccountHistoryListController
from financial.models import AddressNominalAccount, NominalAccountHistory, NominalLedgerDebit, NominalLedgerCredit
from financial.serializers.nominal_account_history import NominalAccountHistorySerializer


__all__ = [
    'NominalAccountHistoryCollection',
]


class NominalAccountHistoryCollection(APIView):
    """
    Handle methods regarding transactions on the Nominal Ledger that use specific Nominal Account Numbers
    """

    def get(self, request: Request, id: int) -> Response:
        """
        summary: Retrieve all amounts debited or credited to a specific Nominal Account

        description: |
            Retrieve all the `amounts` from Nominal Ledger Debits/Credits that reference a specific Nominal Account
            Number, along with the amount outstanding in the Account. Date ranges can be specified for a breakdown of
            Debits and Credits for a Period.

        path_params:
            id:
                description: The Number of a Nominal Account whose Transactions will be listed
                type: integer

        responses:
            200:
                description: A list of Transactions amounts that were debited or credited to a Nominal Account
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieve_requested_object', child_of=request.span):
            # Make sure an Address Account exists with this Account Number before we go trying to find Nominal Ledger
            # Lines
            try:
                obj = AddressNominalAccount.objects.get(
                    address_id=request.user.address['id'],
                    global_nominal_account__nominal_account_number=id,
                )
                account_number = obj.global_nominal_account.nominal_account_number
            except AddressNominalAccount.DoesNotExist:
                return Http404(error_code='financial_nominal_account_history_list_001')

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = NominalAccountHistoryListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the search filters
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span):
            kw = controller.cleaned_data['search']
            order = controller.cleaned_data['order']
            order2 = '-nominal_ledger_id' if order.startswith('-') else 'nominal_ledger_id'
            try:
                objs = NominalAccountHistory.objects.filter(
                    address_id=request.user.address['id'],
                    nominal_account_number=account_number,
                    **kw,
                ).order_by(
                    order,
                    order2,
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_nominal_account_history_list_002')

        with tracer.start_span('calculating_balances', child_of=request.span):
            # First, check if we need to break down the totals by date
            date_filters = dict()
            try:
                # In addition to the User's date filters, we want the transactions before their specified range
                date_filters['transaction_date__lt'] = kw['transaction_date__gte']
            except KeyError:
                try:
                    date_filters['transaction_date__lte'] = kw['transaction_date__gt']
                except KeyError:
                    pass

            if date_filters == {}:
                # They didn't specify any date filters so just get all the transaction amounts
                def get_balances(model):
                    return model.objects.filter(
                        nominal_ledger__address_id=request.user.address['id'],
                        nominal_account_number=account_number,
                    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.0000')

                balances = {
                    'total_credits': get_balances(NominalLedgerCredit) * -1,
                    'total_debits': get_balances(NominalLedgerDebit),
                    'beginning_credits': Decimal('0.0000'),
                    'beginning_debits': Decimal('0.0000'),
                }
                balances.update({
                    'period_credits': balances['total_credits'],
                    'period_debits': balances['total_debits'],
                })

            else:
                # The User specified a date range for the transactions. We'll also fetch the transaction totals leading
                # up to that date range. First construct the filter (a Q object)  that will be used in the aggregation
                period_range = Q()
                for k, v in kw.items():
                    period_range &= Q(**{k: v})

                beginning_range = Q()
                for k, v in date_filters.items():
                    beginning_range &= Q(**{k: v})

                positive = Q(amount__gt=0)
                negative = Q(amount__lt=0)

                # Now go and calculate the balances
                balances = NominalAccountHistory.objects.filter(
                    address_id=request.user.address['id'],
                    nominal_account_number=account_number,
                ).aggregate(
                    beginning_credits=Sum('amount', filter=beginning_range & negative),
                    period_credits=Sum('amount', filter=period_range & negative),
                    total_credits=Sum('amount', filter=negative),
                    beginning_debits=Sum('amount', filter=beginning_range & positive),
                    period_debits=Sum('amount', filter=period_range & positive),
                    total_debits=Sum('amount', filter=positive),
                )

                for k, v in balances.items():
                    if v is None:
                        balances[k] = Decimal('0.0000')

            balances['ending_credits'] = balances['beginning_credits'] + balances['period_credits']
            balances['ending_debits'] = balances['beginning_debits'] + balances['period_debits']

            for k, v in balances.items():
                balances[k] = str(v)

        with tracer.start_span('gathering_metadata', child_of=request.span):
            total_records = objs.count()
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            # Handle Pagination
            objs = objs[page * limit: (page + 1) * limit]
            metadata = {
                'page': page,
                'limit': limit,
                'order': order,
                'warnings': controller.warnings,
                'total_records': total_records,
                **balances,
            }

        with tracer.start_span('calculating_running_balance', child_of=request.span):
            running_balances: Deque = deque()
            if len(objs) > 0:
                # Calculate the sum of the transaction amounts before each transaction
                date_query = Q(transaction_date__lt=objs[0].transaction_date) | \
                    Q(transaction_date=objs[0].transaction_date) & Q(nominal_ledger_id__lte=objs[0].nominal_ledger_id)

                running_balances.append(
                    NominalAccountHistory.objects.filter(
                        date_query,
                        nominal_account_number=account_number,
                        address_id=request.user.address['id'],
                    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.0000'),
                )

                reverse_order = order.startswith('-')
                for i in range(1, len(objs)):
                    if reverse_order:
                        running_balances.append(running_balances[i - 1] - objs[i - 1].amount)
                    else:
                        running_balances.append(running_balances[i - 1] + objs[i].amount)

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = NominalAccountHistorySerializer(
                instance=objs,
                context={
                    'currency_id': obj.currency_id,
                    'running_balances': running_balances,
                },
                many=True,
            ).data

        return Response({'content': data, '_metadata': metadata})
