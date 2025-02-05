"""
Management for Account Sale Credit Notes
"""

# stdlib
from typing import cast
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.utils import db_lock
from django.conf import settings
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.api_view import FinancialAPIView as APIView
from financial.controllers.account_sale_credit_note import (
    AccountSaleCreditNoteContraCreateController,
    AccountSaleCreditNoteCreateController,
    AccountSaleCreditNoteUpdateController,
)
from financial.models import (
    NominalLedger,
    NominalLedgerDebit,
    NominalLedgerCredit,
)
from financial.notifications import Notification
from financial.permissions.account_sale_credit_note import Permissions
from financial.serializers.nominal_ledger import NominalLedgerSerializer


__all__ = [
    'AccountSaleCreditNoteCollection',
    'AccountSaleCreditNoteResource',
    'AccountSaleCreditNoteContraCollection',
    'AccountSaleCreditNoteContraResource',
]


class AccountSaleCreditNoteCollection(APIView):
    """
    Handles methods regarding Account Sale Credit Notes that don't require an id to be specified i.e. create
    """

    serializer_class = NominalLedgerSerializer

    def post(self, request: Request) -> Response:
        """
        summary: Create a Nominal Ledger record where the Transaction Type is for Account Sale Credit Notes

        description: |
            Create a new Nominal Ledger record using data supplied by the User and set the Transaction Type to be
            Account Sale Credit Note

        responses:
            200:
                description: Nominal Ledger entry was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = AccountSaleCreditNoteCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('setting_billing_address', child_of=request.span):
            # Remove the credit, debits, and contra address before calling controller.instance
            credit = controller.cleaned_data.pop('credit')
            debits = controller.cleaned_data.pop('debits')
            contra_address = controller.cleaned_data.pop('contra_address')

            obj = controller.instance
            obj.transaction_type_id = 11003
            obj.address_id = request.user.address['id']
            obj.contact = f'{request.user.first_name} {request.user.surname}'
            obj.address1_bill_to = contra_address['address1']
            obj.address2_bill_to = contra_address['address2']
            obj.address3_bill_to = contra_address['address3']
            obj.name_bill_to = contra_address['name']
            obj.city_bill_to = contra_address['city']
            obj.country_id_bill_to = contra_address['country']['id']
            try:
                obj.subdivision_id_bill_to = contra_address['subdivision']['id']
            except (KeyError, TypeError):
                obj.subdivision_id_bill_to = None

        with tracer.start_span('set_unallocated_balance', child_of=request.span):
            obj.unallocated_balance = credit['amount'] * -1

        with tracer.start_span('saving_objects', child_of=request.span) as span:
            with tracer.start_span('saving_ledger_entry', child_of=span):
                with db_lock(NominalLedger):
                    obj.save()

            with tracer.start_span('saving_debits', child_of=span):
                for debit in debits:
                    NominalLedgerDebit.objects.create(
                        nominal_ledger=obj,
                        **debit,
                    )

            with tracer.start_span('saving_credit', child_of=span):
                NominalLedgerCredit.objects.create(
                    nominal_ledger=obj,
                    **credit,
                )

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        with tracer.start_span('sending_notification', child_of=request.span):
            Notification(token=request.user.token, user=request.user, ledger_data=data).start()

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class AccountSaleCreditNoteResource(APIView):
    """
    Handles methods regarding Account Sale Credit Notes that require an id to be specified i.e. read, update
    """

    serializer_class = NominalLedgerSerializer

    def get(self, request: Request, tsn: int) -> Response:
        """
        summary: Read the details of a specific Account Sale Credit Note record

        description: |
            Attempt to read a Nominal Ledger entry by the given tsn where the Transaction Type is for Account Sale
            Credit Notes, returning a 404 if it does not exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Account Sale Credit Note to read
                type: integer

        responses:
            200:
                description: The Account Sale Credit Note record was read successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_address', child_of=request.span):
            address_id = request.GET.get('address_id')
            if address_id is not None:
                address_id = int(cast(int, address_id))
            else:
                address_id = request.user.address['id']

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.account_sale_credit_notes.get(
                    tsn=tsn,
                    address_id=address_id,
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_account_sale_credit_note_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.read(request, obj, span)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, tsn: int, partial: bool = False) -> Response:
        """
        summary: Update the details of an existing Account Sale Credit Note

        description: |
            Attempt to update the details of an existing Nominal Ledger entry where the Transaction Type is for Account
            Sale Credit Notes, returning a 404 if it doesn't exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Account Sale Credit Note record to be updated
                type: integer

        responses:
            200:
                description: The Account Sale Credit Note record was updated successfully
            400: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.account_sale_credit_notes.get(
                    tsn=tsn,
                    address_id=request.user.address['id'],
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_account_sale_credit_note_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = AccountSaleCreditNoteUpdateController(
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
            data = NominalLedgerSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, tsn: int) -> Response:
        """
        Attempt to partially update an Account Sale Credit Note record
        """
        return self.put(request, tsn, True)


class AccountSaleCreditNoteContraCollection(APIView):
    """
    Handles methods regarding Account Sale Credit Note Contras that don't require an id to be specified, i.e. create
    """

    serializer_class = NominalLedgerSerializer

    def post(self, request: Request, source_id: int) -> Response:
        """
        summary: |
            Create an Account Sale Credit Note on the Nominal Ledger in response to a another Address creating an
            Account Purchase Debit Note with the requesting User's Address.

        description: |
            Create a new Nominal Ledger record using data supplied by the User and set the Transaction Type to be
            Account Sale Credit Note. The data must match the data on the Account Purchase Debit Note that the record
            is being created from.

        path_params:
            source_id:
                description: |
                    The id of an Address that has issued an Account Purchase Debit Note to the requesting User's
                    Address
                type: integer

        responses:
            200:
                description: Nominal Ledger record was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.contra_create(request)
            if err is not None:
                return err

        with tracer.start_span('retrieving_contra_address_record', child_of=request.span) as span:
            response = Membership.address.read(
                token=request.user.token,
                pk=source_id,
                span=span,
            )
            if response.status_code != 200:
                return Http404(error_code='financial_account_sale_credit_note_contra_create_001')
            contra_address = response.json()['content']

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = AccountSaleCreditNoteContraCreateController(data=request.data, request=request, span=span)
            # Set the source_id on the controller as it's required for validating some fields
            controller.address_id = source_id
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('setting_billing_address', child_of=request.span):
            # Remove the credit and debits before calling controller.instance
            credit = controller.cleaned_data.pop('credit')
            debits = controller.cleaned_data.pop('debits')

            obj = controller.instance
            obj.transaction_type_id = 11003
            obj.address_id = request.user.address['id']
            obj.contact = f'{request.user.first_name} {request.user.surname}'
            obj.contra_address_id = contra_address['id']
            obj.address1_bill_to = contra_address['address1']
            obj.address2_bill_to = contra_address['address2']
            obj.address3_bill_to = contra_address['address3']
            obj.city_bill_to = contra_address['city']
            obj.name_bill_to = contra_address['name']
            obj.country_id_bill_to = contra_address['country']['id']
            try:
                obj.subdivision_id_bill_to = contra_address['subdivision']['id']
            except (KeyError, TypeError):
                obj.subdivision_id_bill_to = None

        with tracer.start_span('setting_delivery_address', child_of=request.span):
            debit_note = controller.cleaned_data['contra_nominal_ledger']
            obj.address1_deliver_to = debit_note.address1_deliver_to
            obj.address2_deliver_to = debit_note.address2_deliver_to
            obj.address3_deliver_to = debit_note.address3_deliver_to
            obj.city_deliver_to = debit_note.city_deliver_to
            obj.name_deliver_to = debit_note.name_deliver_to
            obj.country_id_deliver_to = debit_note.country_id_deliver_to
            obj.subdivision_id_deliver_to = debit_note.subdivision_id_deliver_to
            obj.postcode_deliver_to = debit_note.postcode_deliver_to
            obj.contra_contact = debit_note.contact
            obj.external_reference = debit_note.external_reference

        with tracer.start_span('set_unallocated_balance', child_of=request.span):
            obj.unallocated_balance = credit['amount'] * -1

        with tracer.start_span('saving_objects', child_of=request.span) as span:
            with tracer.start_span('saving_nominal_ledger', child_of=span):
                with db_lock(NominalLedger):
                    obj.save()
                debit_note.contra_nominal_ledger = obj
                debit_note.save()

            with tracer.start_span('saving_debits', child_of=span):
                for debit in debits:
                    NominalLedgerDebit.objects.create(
                        nominal_ledger=obj,
                        **debit,
                    )

            with tracer.start_span('saving_credit', child_of=span):
                NominalLedgerCredit.objects.create(
                    nominal_ledger=obj,
                    **credit,
                )

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class AccountSaleCreditNoteContraResource(APIView):
    """
    Handles methods regarding Account Sale Credit Note Contras that do require an id to be specified i.e. read
    """

    serializer_class = NominalLedgerSerializer

    def get(self, request: Request, source_id: int, tsn: int) -> Response:
        """
        summary: |
            Read the details of an Account Sale Credit Note record where the contra address is the same as the
            requesting User's Address

        description: |
            Attempt to read a Nominal Ledger entry where the Transaction Type is for Account Sale Credit Notes, and
            the Contra Address is the requesting User's Address. Returns a 404 if the record does not exist

        path_params:
            source_id:
                description: The id of the Address whose Account Sale Debit Note is being read
                type: integer
            tsn:
                description: The Transaction Sequence Number of the Account Sale Debit Note to read
                type: integer

        responses:
            200:
                description: The Account Sale Debit Note record was read successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.account_sale_credit_notes.get(
                    tsn=tsn,
                    address_id=source_id,
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_account_sale_credit_note_contra_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.contra_read(request, obj, span)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        return Response({'content': data})
