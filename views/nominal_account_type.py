"""
Management for Nominal Account Type
"""

# libs
from cloudcix_rest.exceptions import Http400
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.controllers import NominalAccountTypeListController
from financial.models import NominalAccountType
from financial.serializers import NominalAccountTypeSerializer


__all__ = [
    'NominalAccountTypeCollection',
]


class NominalAccountTypeCollection(APIView):
    """
    Handles methods regarding Nominal Account Type records that do not require an id to be specified, i.e. list
    """

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of Nominal Account Type records

        description: |
            Retrieve a list of Nominal Account Type records that are supported by the CloudCIX platform

        responses:
            200:
                description: A list of Nominal Account Types, filtered and ordered by the User
            400: {}
        """
        tracer = settings.TRACER

        # Create a list controller to parse User data
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = NominalAccountTypeListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the filters
            controller.is_valid()

        # Now get a list of Nominal Account Type records using the filters
        with tracer.start_span('retrieve_requested_objects', child_of=request.span):
            try:
                objs = NominalAccountType.objects.filter(
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_nominal_account_type_list_001')

        with tracer.start_span('generating_metadata', child_of=request.span):
            total_records = objs.count()
            page = controller.cleaned_data['page']
            order = controller.cleaned_data['order']
            limit = controller.cleaned_data['limit']
            warnings = controller.warnings
            metadata = {
                'total_records': total_records,
                'page': page,
                'order': order,
                'limit': limit,
                'warnings': warnings,
            }
            # Handle pagination
            objs = objs[page * limit:(page + 1) * limit]

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = NominalAccountTypeSerializer(instance=objs, many=True).data

        # Generate and return response
        return Response({'content': data, '_metadata': metadata})
