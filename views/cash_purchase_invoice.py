"""
Management for Account Purchase Invoices
"""

# stdlib
from collections import deque
from typing import cast, Deque
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
from financial.controllers.cash_purchase_invoice import (
    CashPurchaseInvoiceContraCreateController,
    CashPurchaseInvoiceCreateController,
    CashPurchaseInvoiceUpdateController,
)
from financial.models import NominalLedger, NominalLedgerCredit, NominalLedgerDebit
from financial.notifications import Notification
from financial.permissions.cash_purchase_invoice import Permissions
from financial.serializers.nominal_ledger import NominalLedgerSerializer


__all__ = [
    'CashPurchaseInvoiceCollection',
    'CashPurchaseInvoiceResource',
    'CashPurchaseInvoiceContraCollection',
    'CashPurchaseInvoiceContraResource',
]


class CashPurchaseInvoiceCollection(APIView):
    """
    Handles methods regarding Cash Purchase Invoices that don't require an id to be specified i.e. create
    """

    serializer_class = NominalLedgerSerializer

    def post(self, request: Request) -> Response:
        """
        summary: Create a Nominal Ledger record where the Transaction Type is for Cash Purchase Invoices

        description: |
            Create a new Nominal Ledger record using data supplied by the User and set the Transaction Type to be for
            Cash Purchase Invoices

        responses:
            200:
                description: Nominal Ledger record was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = CashPurchaseInvoiceCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('setting_billing_address', child_of=request.span):
            # Remove the debits, credit, contra address, and address account before calling controller.instance
            debits = controller.cleaned_data.pop('debits')
            credit = controller.cleaned_data.pop('credit')
            contra_address = controller.cleaned_data.pop('contra_address')
            address_account = controller.cleaned_data.pop('address_account')

            obj = controller.instance
            obj.transaction_type_id = 10000
            obj.address_id = request.user.address['id']
            obj.contact = f'{request.user.first_name} {request.user.surname}'
            obj.address1_bill_to = contra_address['address1']
            obj.address2_bill_to = contra_address['address2']
            obj.address3_bill_to = contra_address['address3']
            obj.city_bill_to = contra_address['city']
            obj.name_bill_to = contra_address['name']
            obj.postcode_bill_to = contra_address['postcode']
            obj.country_id_bill_to = contra_address['country']['id']
            try:
                obj.subdivision_id_bill_to = contra_address['subdivision']['id']
            except (KeyError, TypeError):
                obj.subdivision_id_bill_to = None

        with tracer.start_span('saving_objects', child_of=request.span) as span:
            with tracer.start_span('saving_ledger_entry', child_of=span):
                with db_lock(NominalLedger):
                    obj.save()

            with tracer.start_span('saving_debits', child_of=span):
                lines: Deque = deque()
                for debit in debits:
                    lines.append(NominalLedgerDebit(
                        nominal_ledger=obj,
                        **debit,
                    ))
                NominalLedgerDebit.objects.bulk_create(lines)

            with tracer.start_span('saving_credit', child_of=span):
                NominalLedgerCredit.objects.create(
                    description=address_account.description,
                    nominal_account_number=address_account.global_nominal_account.nominal_account_number,
                    nominal_ledger=obj,
                    **credit,
                )

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        with tracer.start_span('sending_notification', child_of=request.span):
            Notification(token=request.user.token, user=request.user, ledger_data=data).start()

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class CashPurchaseInvoiceResource(APIView):
    """
    Handles methods regarding Cash Purchase Debit Notes that do require an id to be specified i.e. read, update
    """

    serializer_class = NominalLedgerSerializer

    def get(self, request: Request, tsn: int) -> Response:
        """
        summary: Read the details of a specific Cash Purchase Invoice record

        description: |
            Attempt to read a Nominal Ledger entry by the given tsn where the Transaction Type is for Cash Purchase
            Invoices, returning a 404 if it does not exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Cash Purchase Invoice to read
                type: integer

        responses:
            200:
                description: The Cash Purchase Invoice record was read successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            address_id = request.GET.get('address_id', request.user.address['id'])
            try:
                obj = NominalLedger.cash_purchase_invoices.get(
                    tsn=tsn,
                    address_id=int(cast(int, address_id)),
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_cash_purchase_invoice_read_001')
            except (TypeError, ValueError):
                return Http400(errors={'address_id': {'error_code': 'financial_cash_purchase_invoice_read_002'}})

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.read(request, obj, span)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, tsn: int, partial: bool = False) -> Response:
        """
        summary: Update the details of an existing Cash Purchase Invoice

        description: |
            Attempt to update the details of an existing Nominal Ledger entry where the Transaction Type is for Cash
            Purchase Invoices, returning a 404 if it doesn't exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Cash Purchase Invoice record to be updated
                type: integer

        responses:
            200:
                description: The Cash Purchase Invoice record was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.cash_purchase_invoices.get(
                    tsn=tsn,
                    address_id=request.user.address['id'],
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_cash_purchase_invoice_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = CashPurchaseInvoiceUpdateController(
                data=request.data,
                request=request,
                instance=obj,
                partial=partial,
                span=span,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        return Response({'content': data})

    def patch(self, request: Request, tsn: int) -> Response:
        """
        Attempt to partially update a Cash Purchase Invoice record
        """
        return self.put(request, tsn, True)


class CashPurchaseInvoiceContraCollection(APIView):
    """
    Handles methods regarding Cash Purchase Invoice Contras that don't require an id to be specified i.e. create
    """

    serializer_class = NominalLedgerSerializer

    def post(self, request: Request, source_id: int) -> Response:
        """
        summary: |
            Create a Cash Purchase Invoice on the Nominal Ledger in response to another Address creating a Cash Sale
             Invoice with the requesting User's Address.

        description: |
            Create a new Nominal Ledger record using data supplied by the User and set the Transaction Type to be for
            Cash Purchase Invoices. The data must match the data on the Cash Sale Invoice that the record is being
            created from

        path_params:
            source_id:
                description: |
                    The id of an Address that has issued a Cash Sale Invoice to the requesting User's Address
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
                return Http404(error_code='financial_cash_purchase_invoice_contra_create_001')
            contra_address = response.json()['content']

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = CashPurchaseInvoiceContraCreateController(data=request.data, request=request, span=span)
            # Set the source_id on the controller as it's needed for validating some fields
            controller.address_id = source_id
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('setting_billing_address', child_of=request.span):
            # Remove the debits, credit, and address account before calling controller.instance
            debits = controller.cleaned_data.pop('debits')
            credit = controller.cleaned_data.pop('credit')
            address_account = controller.cleaned_data.pop('address_account')

            obj = controller.instance
            obj.transaction_type_id = 10000
            obj.address_id = request.user.address['id']
            obj.contact = f'{request.user.first_name} {request.user.surname}'
            obj.contra_address_id = contra_address['id']
            obj.address1_bill_to = contra_address['address1']
            obj.address2_bill_to = contra_address['address2']
            obj.address3_bill_to = contra_address['address3']
            obj.address3_bill_to = contra_address['address3']
            obj.city_bill_to = contra_address['city']
            obj.name_bill_to = contra_address['name']
            obj.postcode_bill_to = contra_address['postcode']
            obj.country_id_bill_to = contra_address['country']['id']
            try:
                obj.subdivision_id_bill_to = contra_address['subdivision']['id']
            except (KeyError, TypeError):
                obj.subdivision_id_bill_to = None

        with tracer.start_span('setting_delivery_address', child_of=request.span):
            sale_invoice = controller.cleaned_data['contra_nominal_ledger']
            obj.address1_deliver_to = sale_invoice.address1_deliver_to
            obj.address2_deliver_to = sale_invoice.address2_deliver_to
            obj.address3_deliver_to = sale_invoice.address3_deliver_to
            obj.city_deliver_to = sale_invoice.city_deliver_to
            obj.name_deliver_to = sale_invoice.name_deliver_to
            obj.postcode_deliver_to = sale_invoice.postcode_deliver_to
            obj.country_id_deliver_to = sale_invoice.country_id_deliver_to
            obj.subdivision_id_deliver_to = sale_invoice.subdivision_id_deliver_to

            obj.contra_contact = sale_invoice.contact
            obj.narrative = sale_invoice.narrative
            obj.external_reference = sale_invoice.external_reference

        with tracer.start_span('saving_objects', child_of=request.span) as span:
            with tracer.start_span('saving_ledger_entry', child_of=span):
                with db_lock(NominalLedger):
                    obj.save()
                sale_invoice.contra_nominal_ledger = obj
                sale_invoice.save()

            with tracer.start_span('saving_debits', child_of=span):
                lines: Deque = deque()
                for debit in debits:
                    lines.append(NominalLedgerDebit(
                        nominal_ledger=obj,
                        **debit,
                    ))
                NominalLedgerDebit.objects.bulk_create(lines)

            with tracer.start_span('saving_credits', child_of=span):
                NominalLedgerCredit.objects.create(
                    description=address_account.description,
                    nominal_account_number=address_account.global_nominal_account.nominal_account_number,
                    nominal_ledger=obj,
                    **credit,
                )

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class CashPurchaseInvoiceContraResource(APIView):
    """
    Handles methods regarding Cash Purchase Invoice Contras that do require an id to be specified i.e. read
    """

    serializer_class = NominalLedgerSerializer

    def get(self, request: Request, tsn: int, source_id: int) -> Response:
        """
        summary: |
            Read the details of a Cash Purchase Invoice record where the Contra Address is the same as the
            requesting User's Address

        description: |
            Attempt to read a Nominal Ledger entry by the given tsn where the Transaction Type is for Cash Purchase
            Invoices, and the Contra Address is the requesting User's Address. Returns a 404 if it does not exist

        path_params:
            source_id:
                description: The id of the Address whose Cash Purchase Invoice is being read
                type: integer
            tsn:
                description: The Transaction Sequence Number of the Cash Purchase Invoice to read
                type: integer

        responses:
            200:
                description: The Cash Purchase Invoice record was read successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.cash_purchase_invoices.get(
                    tsn=tsn,
                    address_id=source_id,
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_cash_purchase_invoice_contra_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.contra_read(request, obj, span)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        return Response({'content': data})
