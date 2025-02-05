"""
Management for Account Sale Adjustments
"""

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
from financial.controllers.account_sale_adjustment import (
    AccountSaleAdjustmentCreateController,
    AccountSaleAdjustmentContraCreateController,
)
from financial.models import (
    NominalLedger,
    NominalLedgerDebit,
    NominalLedgerCredit,
)
from financial.notifications import Notification
from financial.permissions.account_sale_adjustment import Permissions
from financial.serializers.nominal_ledger import NominalLedgerSerializer


__all__ = [
    'AccountSaleAdjustmentCollection',
    'AccountSaleAdjustmentContraCollection',
    'AccountSaleAdjustmentResource',
    'AccountSaleAdjustmentContraResource',
]


class AccountSaleAdjustmentCollection(APIView):
    """
    Handles methods regarding Account Sale Adjustments that don't require an id to be specified, i.e. create
    """

    serializer_class = NominalLedgerSerializer

    def post(self, request: Request) -> Response:
        """
        summary: Create a Nominal Ledger record where the Transaction Type is for Account Sale Adjustments

        description: |
            Create a new Nominal Ledger record using data supplied by the User and set the Transaction Type to be
            Account Sale Adjustment.

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
            controller = AccountSaleAdjustmentCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('setting_billing_address', child_of=request.span):
            # Remove debit, credit, and contra address before calling controller.instance.
            debit = controller.cleaned_data.pop('debit')
            credit = controller.cleaned_data.pop('credit')
            contra_address = controller.cleaned_data.pop('contra_address')

            # For each attribute in the contra_address, add it to the instance as billing info
            obj = controller.instance
            obj.transaction_type_id = 11005
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

        with tracer.start_span('saving_object', child_of=request.span) as span:
            with tracer.start_span('saving_ledger_entry', child_of=span):
                with db_lock(NominalLedger):
                    obj.save()

            # Save the debit and credit entries
            with tracer.start_span('saving_debit', child_of=span):
                NominalLedgerDebit.objects.create(
                    amount=debit['amount'],
                    exchange_rate=1,
                    nominal_ledger=obj,
                    nominal_account_number=debit['number'],
                )

            with tracer.start_span('saving_credit', child_of=span):
                NominalLedgerCredit.objects.create(
                    amount=credit['amount'],
                    exchange_rate=1,
                    nominal_ledger=obj,
                    nominal_account_number=credit['number'],
                )

        with tracer.start_span('serializing_data', child_of=span):
            data = NominalLedgerSerializer(instance=obj).data

        with tracer.start_span('sending_notification', child_of=request.span):
            Notification(token=request.user.token, user=request.user, ledger_data=data).start()

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class AccountSaleAdjustmentResource(APIView):
    """
    Handles methods regarding Account Sale Adjustments that require an id to be specified, i.e. read
    """

    serializer_class = NominalLedgerSerializer

    def get(self, request: Request, tsn: int) -> Response:
        """
        summary: Read the details of a specific Account Sale Adjustment record

        description: |
            Attempt to read a Nominal Ledger entry where the Transaction Type is for Account Sale Adjustments,
            returning a 404 if it does not exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Account Sale Adjustment record to be retrieved
                type: integer

        responses:
            200:
                description: The Account Sale Adjustment record was read successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.account_sale_adjustments.get(
                    tsn=tsn,
                    address_id=request.user.address['id'],
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_account_sale_adjustment_read_001')

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        return Response({'content': data})


class AccountSaleAdjustmentContraCollection(APIView):
    """
    Handles methods regarding Account Sale Adjustment Contras that don't require an id to be specified, i.e. create
    """

    serializer_class = NominalLedgerSerializer

    def post(self, request: Request, source_id: int) -> Response:
        """
        summary: |
            Create an Account Sale Adjustment on the Nominal Ledger in response to a another Address creating an
            Account Purchase Adjustment with the requesting User's Address

        description: |
            Create a new Nominal Ledger record using data supplied by the User and set the Transaction Type to be
            Account Sale Adjustment.

        path_params:
            source_id:
                description: |
                    The id of an Address that has issued an Account Purchase Adjustment to the requesting User's
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

        with tracer.start_span('retrieving_contra_address_record', child_of=request.span):
            response = Membership.address.read(
                token=request.user.token,
                pk=source_id,
            )
            if response.status_code != 200:
                return Http404(error_code='financial_account_sale_adjustment_contra_create_001')
            contra_address = response.json()['content']

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = AccountSaleAdjustmentContraCreateController(data=request.data, request=request, span=span)
            # Set the source_id on the controller as it's needed for validating some fields
            controller.address_id = source_id
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('set_billing_address', child_of=request.span):
            # Remove the debit and credit before calling controller.instance
            credit = controller.cleaned_data.pop('credit')
            debit = controller.cleaned_data.pop('debit')

            obj = controller.instance
            obj.transaction_type_id = 11005
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

        with tracer.start_span('set_delivery_address', child_of=request.span):
            purchase_adjustment = obj.contra_nominal_ledger
            obj.address1_deliver_to = purchase_adjustment.address1_deliver_to
            obj.address2_deliver_to = purchase_adjustment.address2_deliver_to
            obj.address3_deliver_to = purchase_adjustment.address3_deliver_to
            obj.name_deliver_to = purchase_adjustment.name_deliver_to
            obj.city_deliver_to = purchase_adjustment.city_deliver_to
            obj.country_id_deliver_to = purchase_adjustment.country_id_deliver_to
            obj.subdivision_id_deliver_to = purchase_adjustment.subdivision_id_deliver_to
            obj.postcode_deliver_to = purchase_adjustment.postcode_deliver_to
            obj.external_reference = purchase_adjustment.external_reference

        with tracer.start_span('saving_object', child_of=request.span) as span:
            with tracer.start_span('saving_ledger_entry', child_of=span):
                with db_lock(NominalLedger):
                    obj.save()
                purchase_adjustment.contra_nominal_ledger = obj
                purchase_adjustment.save()

            # Save the debit and credit entries
            with tracer.start_span('saving_debit', child_of=span):
                NominalLedgerDebit.objects.create(
                    amount=debit['amount'],
                    exchange_rate=1,
                    nominal_ledger=obj,
                    nominal_account_number=debit['number'],
                )

            with tracer.start_span('saving_credit', child_of=span):
                NominalLedgerCredit.objects.create(
                    amount=credit['amount'],
                    exchange_rate=1,
                    nominal_ledger=obj,
                    nominal_account_number=credit['number'],
                )

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class AccountSaleAdjustmentContraResource(APIView):
    """
    Handles methods regarding Account Sale Adjustment Contras that require an id to be specified, i.e. read
    """

    serializer_class = NominalLedgerSerializer

    def get(self, request: Request, source_id: int, tsn: int) -> Response:
        """
        summary: |
            Read an Account Sale Adjustment record where the Contra Address is the same as the requesting User's Address

        description: |
            Attempt to read a Nominal Ledger entry where the Transaction Type is Account Sale Adjustment, and the
            Contra Address is the requesting User's Address. Returns a 404 if the record does not exist

        path_params:
            source_id:
                description: The id of the Address whose Account Sale Adjustment is being read
                type: integer
            tsn:
                description: The Transaction Sequence Number of the Account Sale Adjustment to read
                type: integer

        responses:
            200:
                description: Nominal Ledger record was created successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.account_sale_adjustments.get(
                    tsn=tsn,
                    address_id=source_id,
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_account_sale_adjustment_contra_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.contra_read(request, obj)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        return Response({'content': data})
