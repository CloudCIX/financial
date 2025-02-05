"""
Management for Account Purchase Payments
"""

# stdlib
from decimal import Decimal
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
from financial import reserved_accounts as reserved
from financial.controllers.account_purchase_payment import (
    AccountPurchasePaymentContraCreateController,
    AccountPurchasePaymentCreateController,
)
from financial.models import NominalLedger, NominalLedgerCredit, NominalLedgerDebit
from financial.notifications import Notification
from financial.permissions.account_purchase_payment import Permissions
from financial.serializers.nominal_ledger import NominalLedgerSerializer


__all__ = [
    'AccountPurchasePaymentCollection',
    'AccountPurchasePaymentResource',
    'AccountPurchasePaymentContraCollection',
    'AccountPurchasePaymentContraResource',
]


class AccountPurchasePaymentCollection(APIView):
    """
    Handles methods regarding Account Purchase Payments that don't require an id to be specified i.e. create
    """

    serializer_class = NominalLedgerSerializer

    def post(self, request: Request) -> Response:
        """
        summary: Create a Nominal Ledger record where the Transaction Type is for Account Purchase Payments

        description: |
            Create a new Nominal Ledger record using data supplied by the User and set the Transaction Type to be
            Account Purchase Payment

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
            controller = AccountPurchasePaymentCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('setting_billing_address', child_of=request.span):
            # Remove the contra address, nominal account number, amount and exchange rate before calling
            # controller.instance
            contra_address = controller.cleaned_data.pop('contra_address')
            nominal_account_number = controller.cleaned_data.pop('nominal_account_number')
            amount = controller.cleaned_data.pop('amount')
            exchange_rate = controller.cleaned_data.pop('exchange_rate', Decimal('1'))

            obj = controller.instance
            obj.transaction_type_id = 10004
            obj.address_id = request.user.address['id']
            obj.contact = f'{request.user.first_name} {request.user.surname}'
            obj.address1_bill_to = contra_address['address1']
            obj.address2_bill_to = contra_address['address2']
            obj.address3_bill_to = contra_address['address3']
            obj.name_bill_to = contra_address['name']
            obj.city_bill_to = contra_address['city']
            obj.postcode_bill_to = contra_address['postcode']
            obj.country_id_bill_to = contra_address['country']['id']
            try:
                obj.subdivision_id_bill_to = contra_address['subdivision']['id']
            except (KeyError, TypeError):
                obj.subdivision_id_bill_to = None

        with tracer.start_span('set_unallocated_balance', child_of=request.span):
            base_currency_amount = (amount * exchange_rate).quantize(Decimal('1.0000'))
            obj.unallocated_balance = base_currency_amount

        with tracer.start_span('saving_objects', child_of=request.span) as span:
            with tracer.start_span('saving_ledger_entry', child_of=span):
                with db_lock(NominalLedger):
                    obj.save()

            with tracer.start_span('saving_debit', child_of=span):
                NominalLedgerDebit.objects.create(
                    amount=base_currency_amount,
                    exchange_rate=1,
                    nominal_account_number=reserved.CREDITOR_CONTROL_ACCOUNT,
                    nominal_ledger=obj,
                )

            with tracer.start_span('saving_credit', child_of=span):
                NominalLedgerCredit.objects.create(
                    amount=amount,
                    exchange_rate=exchange_rate,
                    nominal_account_number=nominal_account_number,
                    nominal_ledger=obj,
                )

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        with tracer.start_span('sending_notification', child_of=request.span):
            Notification(token=request.user.token, user=request.user, ledger_data=data).start()

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class AccountPurchasePaymentResource(APIView):
    """
    Handles methods regarding Account Purchase Payments that do require an id to be specified i.e. read
    """

    serializer_class = NominalLedgerSerializer

    def get(self, request: Request, tsn: int) -> Response:
        """
        summary: Read a Nominal Ledger record where the Transaction Type is for Account Purchase Payments

        description: |
            Read new Nominal Ledger where the Transaction Type is for Account Purchase Payments, returning a 404 if it
            does not exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Account Purchase Payment to read
                type: integer

        responses:
            200:
                description: Nominal Ledger record was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_address_id', child_of=request.span):
            address_id = request.GET.get('address_id')
            if address_id is not None:
                address_id = int(cast(int, address_id))
            else:
                address_id = request.user.address['id']

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.account_purchase_payments.get(
                    address_id=address_id,
                    tsn=tsn,
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_account_purchase_payment_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.read(request, obj, span)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        return Response({'content': data})


class AccountPurchasePaymentContraCollection(APIView):
    """
    Handles methods regarding Account Purchase Payment Contras that don't require an id to be specified i.e. create
    """

    serializer_class = NominalLedgerSerializer

    def post(self, request: Request, source_id: int) -> Response:
        """
        summary: |
            Create an Account Purchase Payment on the Nominal Ledger in response to a another Address creating an
            Account Sale Payment with the requesting User's Address

        description: |
            Create a new Nominal Ledger record using data supplied by the User and set the Transaction Type to be
            Account Purchase Payment.

        path_params:
            source_id:
                description: |
                    The id of an Address that has issued an Account Sale Payment to the requesting User's Address
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

        with tracer.start_span('retrieving_contra_address_record', child_of=request.span):
            response = Membership.address.read(
                token=request.user.token,
                pk=source_id,
            )
            if response.status_code != 200:
                return Http404(error_code='financial_account_purchase_payment_contra_create_001')
            contra_address = response.json()['content']

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = AccountPurchasePaymentContraCreateController(data=request.data, request=request, span=span)
            # Set the source id on the controller as it's needed for validating some fields
            controller.address_id = source_id
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('setting_billing_address', child_of=request.span):
            # Remove the nominal account number and exchange rate before calling controller.instance
            nominal_account_number = controller.cleaned_data.pop('nominal_account_number')
            exchange_rate = controller.cleaned_data.pop('exchange_rate', Decimal('1'))

            obj = controller.instance
            obj.transaction_type_id = 10004
            obj.address_id = request.user.address['id']
            obj.contact = f'{request.user.first_name} {request.user.surname}'
            obj.contra_address_id = contra_address['id']
            obj.address1_bill_to = contra_address['address1']
            obj.address2_bill_to = contra_address['address2']
            obj.address3_bill_to = contra_address['address3']
            obj.name_bill_to = contra_address['name']
            obj.city_bill_to = contra_address['city']
            obj.postcode_bill_to = contra_address['postcode']
            obj.country_id_bill_to = contra_address['country']['id']
            try:
                obj.subdivision_id_bill_to = contra_address['subdivision']['id']
            except (KeyError, TypeError):
                obj.subdivision_id_bill_to = None

        with tracer.start_span('fetching_transaction_amount', child_of=request.span):
            # Get the amount that was transferred in the Contra Transaction
            amount = obj.contra_nominal_ledger.debits.first().amount
            base_currency_amount = (amount * exchange_rate).quantize(Decimal('1.00'))

        with tracer.start_span('saving_objects', child_of=request.span) as span:
            with tracer.start_span('saving_ledger_entry', child_of=span):
                with db_lock(NominalLedger):
                    obj.save()
                sale_payment = obj.contra_nominal_ledger
                sale_payment.contra_nominal_ledger = obj
                sale_payment.save()

            with tracer.start_span('saving_debit', child_of=span):
                NominalLedgerDebit.objects.create(
                    amount=base_currency_amount,
                    exchange_rate=1,
                    nominal_account_number=reserved.CREDITOR_CONTROL_ACCOUNT,
                    nominal_ledger=obj,
                )

            with tracer.start_span('saving_credit', child_of=span):
                NominalLedgerCredit.objects.create(
                    amount=amount,
                    exchange_rate=exchange_rate,
                    nominal_account_number=nominal_account_number,
                    nominal_ledger=obj,
                )

            with tracer.start_span('saving_unallocated_balance', child_of=span):
                obj.unallocated_balance = base_currency_amount
                obj.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class AccountPurchasePaymentContraResource(APIView):
    """
    Handles methods regarding Account Purchase Payment Contras that do require an id to be specified i.e. read
    """

    serializer_class = NominalLedgerSerializer

    def get(self, request: Request, source_id: int, tsn: int) -> Response:
        """
        summary: |
            Read an Account Purchase Payment record where the Contra Address is the same as the requesting User's
            Address

        description: |
            Attempt to read a Nominal Ledger entry where the Transaction Type is for Account Purchase Payments, and the
            Contra Address is the requesting User's Address. Returns a 404 if the record does not exist

        path_params:
            source_id:
                description: The id of the Address whose Account Purchase Payment is being read
                type: integer
            tsn:
                description: The Transaction Sequence Number of the Account Purchase Payment to read
                type: integer

        responses:
            200:
                description: Nominal Ledger record was read successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.account_purchase_payments.get(
                    tsn=tsn,
                    address_id=source_id,
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_account_purchase_payment_contra_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.contra_read(request, obj, span)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        return Response({'content': data})
