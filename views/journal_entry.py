"""
Management for Journal Entries
"""
# stdlib
from collections import deque
from typing import Deque
# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.utils import db_lock
from django.db.models import Sum
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.controllers.journal_entry import (
    JournalEntryCreateController,
    JournalEntryListController,
    JournalEntryUpdateController,
)
from financial.api_view import FinancialAPIView as APIView
from financial.models import NominalLedger, NominalLedgerCredit, NominalLedgerDebit
from financial.notifications import Notification
from financial.permissions.journal_entry import Permissions
from financial.serializers.journal_entry import JournalEntrySerializer


__all__ = [
    'JournalEntryCollection',
    'JournalEntryResource',
]


class JournalEntryCollection(APIView):
    """
    Handles methods regarding Journal Entries on the Nominal Ledger that don't require an id to be specified
    """

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of Journal Entries

        description: Retrieve a list of Journal Entries from the Nominal Ledger

        responses:
            200:
                description: A list of Journal Entry transactions, filtered and ordered by the User
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = JournalEntryListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the filters
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span) as span:
            order = controller.cleaned_data['order']
            try:
                objs = NominalLedger.journal_entries.filter(
                    address_id=request.user.address['id'],
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    order,
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_journal_entry_list_001')

        with tracer.start_span('gathering_metadata', child_of=request.span):
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            total_records = objs.count()
            # Handle pagination
            objs = objs[page * limit: (page + 1) * limit]

            # Get the total debits and credits. For some reason the models need to be switched for the metadata... This
            # is how it was done in the PY2 version. It shouldn't make a difference anyway since if everything is
            # working as intended then the total credits should equal the total debits
            total_credits = NominalLedgerDebit.objects.filter(
                nominal_ledger__address_id=request.user.address['id'],
                nominal_ledger__transaction_type_id=12000,
            ).aggregate(
                balance=Sum('amount'),
            )['balance']

            total_debits = NominalLedgerCredit.objects.filter(
                nominal_ledger__address_id=request.user.address['id'],
                nominal_ledger__transaction_type_id=12000,
            ).aggregate(
                balance=Sum('amount'),
            )['balance']

            metadata = {
                'page': page,
                'limit': limit,
                'order': order,
                'total_records': total_records,
                'total_credits': str(total_credits),
                'total_debits': str(total_debits),
            }

        with tracer.start_span('serializing_data', child_of=request.span):
            span.set_tag('num_objects', objs.count())
            data = JournalEntrySerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a Journal Entry

        description: Create a Journal Entry transaction on the Nominal Ledger using data supplied by the User

        responses:
            201:
                description: Journal Entry was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = JournalEntryCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('setting_billing_address', child_of=request.span):
            # Remove the credits and debits from the cleaned data before calling controller.instance
            credits = controller.cleaned_data.pop('credits')
            debits = controller.cleaned_data.pop('debits')

            address = request.user.address

            obj = controller.instance
            obj.transaction_type_id = 12000
            obj.address_id = address['id']
            obj.address1_bill_to = address['address1']
            obj.address2_bill_to = address['address2']
            obj.address3_bill_to = address['address3']
            obj.city_bill_to = address['city']
            obj.contact = f'{request.user.first_name} {request.user.surname}'
            obj.contra_address_id = address['id']
            obj.country_id_bill_to = address['country_id']
            obj.name_bill_to = address['name']
            obj.postcode_bill_to = address['postcode']
            try:
                obj.subdivision_id_bill_to = address['subdivision_id']
            except (KeyError, TypeError):  # pragma: no cover
                obj.subdivision_id_bill_to = None

        with tracer.start_span('saving_objects', child_of=request.span) as span:
            with tracer.start_span('saving_ledger_entry', child_of=span):
                with db_lock(NominalLedger):
                    obj.save()

            with tracer.start_span('saving_debits', child_of=span):
                lines: Deque = deque()
                for debit in debits:
                    lines.append(NominalLedgerDebit(
                        amount=debit['amount'],
                        nominal_account_number=debit['number'],
                        nominal_ledger=obj,
                    ))
                NominalLedgerDebit.objects.bulk_create(lines)

            with tracer.start_span('saving_credits', child_of=span):
                lines = deque()
                for credit in credits:
                    lines.append(NominalLedgerCredit(
                        amount=credit['amount'],
                        nominal_account_number=credit['number'],
                        nominal_ledger=obj,
                    ))
                NominalLedgerCredit.objects.bulk_create(lines)

        with tracer.start_span('serializing_data', child_of=request.span):
            data = JournalEntrySerializer(instance=obj).data

        with tracer.start_span('sending_notification', child_of=request.span):
            Notification(token=request.user.token, user=request.user, ledger_data=data).start()

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class JournalEntryResource(APIView):
    """
    Handles methods regarding Journal Entries that require an id to be specified
    """

    def get(self, request: Request, tsn: int) -> Response:
        """
        summary: Read the details of a specified Journal Entry

        description: |
            Attempt to read a Nominal Ledger entry by the given tsn where the Transaction Type is for Journal Entries,
            returning a 404 if it does not exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Journal Entry to be read
                type: integer

        responses:
            200:
                description: Journal Entry was read successfully
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieve_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.journal_entries.get(
                    address_id=request.user.address['id'],
                    tsn=tsn,
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_journal_entry_read_001')

        with tracer.start_span('serializing_data', child_of=request.span):
            data = JournalEntrySerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, tsn: int, partial: bool = False) -> Response:
        """
        summary: Update the details of a specified Journal Entry

        description: |
            Attempt to update the details of an existing Nominal Ledger entry where the Transaction Type is for Journal
            Entries, returning a 404 if it doesn't exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Journal Entry to update
                type: integer

        responses:
            200:
                description: Journal Entry was updated successfully
            400: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.journal_entries.get(
                    address_id=request.user.address['id'],
                    tsn=tsn,
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_journal_entry_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = JournalEntryUpdateController(
                instance=obj,
                data=request.data,
                request=request,
                partial=partial,
                span=span,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = JournalEntrySerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, tsn: int) -> Response:
        """
        Attempt to partially update a Journal Entry record
        """
        return self.put(request, tsn, True)
