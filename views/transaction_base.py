"""
Base classes for financial transactions
"""

# libs
from cloudcix_rest.exceptions import Http400, Http404
from django.conf import settings
from cloudcix_rest.utils import db_lock
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.models import NominalLedger
from financial.notifications import Notification
from financial.serializers import NominalLedgerSerializer
from financial.api_view import FinancialAPIView as APIView


class Collection(APIView):
    """
    A base class for financial transactions that do not require an id to be specified
    """

    serializer_class = NominalLedgerSerializer

    def __init__(self, create_controller, transaction_type_id, permissions, *args, **kwargs):
        super(Collection, self).__init__(*args, **kwargs)
        self._create_controller = create_controller
        self._transaction_type_id = transaction_type_id
        self._permissions = permissions

    def _post(self, request: Request) -> Response:
        """
        Basic POST method for transactions
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = self._permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = self._create_controller(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('setting_extra_ledger_data', child_of=request.span):
            popped_data = self._pop_cleaned_data(controller)

            obj = controller.instance
            obj.transaction_type_id = self._transaction_type_id
            obj.address_id = request.user.address['id']
            obj.contact = f'{request.user.first_name} {request.user.surname}'

        self._pre_save_operations(request, obj, popped_data)

        with tracer.start_span('saving_object', child_of=request.span) as span:
            with tracer.start_span('saving_ledger_entry', child_of=span):
                with db_lock(NominalLedger):
                    obj.save()

            # Save the debit and credit entries
            with tracer.start_span('saving_debits', child_of=span):
                self._save_debits(obj, popped_data)

            with tracer.start_span('saving_credits', child_of=span):
                self._save_credits(obj, popped_data)

        with tracer.start_span('serializing_data', child_of=span):
            data = NominalLedgerSerializer(instance=obj).data

        with tracer.start_span('sending_notification', child_of=request.span):
            # Send out notifications only if the transaction uses a contra address id
            if data['contra_address_id']:
                Notification(token=request.user.token, user=request.user, ledger_data=data).start()  # pragma: no cover

        return Response({'content': data}, status=status.HTTP_201_CREATED)

    def _pop_cleaned_data(self, cleaned_data):
        """
        If the controller sets cleaned data that does not belong on a Nominal Ledger object, use this method to pop it
        from the dictionary
        """
        raise NotImplementedError  # pragma: no cover

    def _pre_save_operations(self, request, ledger_obj, popped_data):
        """
        Override this class if there are any other operations that need to be done before saving the ledger objects
        """
        pass  # pragma: no cover

    def _set_billing_address(self, ledger_obj, contra_address):  # pragma: no cover
        ledger_obj.address1_bill_to = contra_address['address1']
        ledger_obj.address2_bill_to = contra_address['address2']
        ledger_obj.address3_bill_to = contra_address['address3']
        ledger_obj.name_bill_to = contra_address['name']
        ledger_obj.city_bill_to = contra_address['city']
        ledger_obj.postcode_bill_to = contra_address['postcode']
        ledger_obj.country_id_bill_to = contra_address['country']['id']
        try:
            ledger_obj.subdivision_id_bill_to = contra_address['subdivision']['id']
        except (KeyError, TypeError):
            ledger_obj.subdivision_id_bill_to = None

    def _save_debits(self, ledger_obj, popped_data):
        raise NotImplementedError  # pragma: no cover

    def _save_credits(self, ledger_obj, popped_data):
        raise NotImplementedError  # pragma: no cover


class Resource(APIView):
    """
    Base class for financial transactions that don't require an id to be specified
    """
    serializer_class = NominalLedgerSerializer

    def __init__(self, transaction_type_id, permissions, read_params, update_params, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)
        self._transaction_type_id = transaction_type_id
        self._permissions = permissions

        if read_params is not None:
            self._read_err_code = read_params[0]
        else:  # pragma: no cover
            self._read_err_code = None

        if update_params is not None:
            self._update_err_code = update_params[0]
            self._update_controller = update_params[1]
        else:  # pragma: no cover
            self._update_err_code = None
            self._update_controller = None

    def _get(self, request: Request, tsn: int) -> Response:
        """
        Basic GET method for transactions
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.objects.get(
                    transaction_type_id=self._transaction_type_id,
                    tsn=tsn,
                    address_id=request.user.address['id'],
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code=self._read_err_code)

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalLedgerSerializer(instance=obj).data

        return Response({'content': data})

    def _put(self, request: Request, tsn: int, partial: bool = False) -> Response:
        """
        Basic PUT method for transactions
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.objects.get(
                    transaction_type_id=self._transaction_type_id,
                    tsn=tsn,
                    address_id=request.user.address['id'],
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code=self._update_err_code)

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = self._permissions.update(obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = self._update_controller(
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
