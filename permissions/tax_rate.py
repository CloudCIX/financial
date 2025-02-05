# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from financial.models.tax_rate import TaxRate


__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create a Tax Rate is valid if:
        - The requesting User's Member is self-managed
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_tax_rate_create_201')

        return None

    @staticmethod
    def read(request: Request, obj: TaxRate, span) -> Optional[Http403]:
        """
        The request to read a Tax Rate is valid if:
        - The Tax Rate record is from the requesting User's Address
        """
        # The Tax Rate record is from the requesting User's Address
        if request.user.address['id'] != obj.address_id:
            return Http403(error_code='financial_tax_rate_read_201')

        return None

    @staticmethod
    def update(request: Request, obj: TaxRate) -> Optional[Http403]:
        """
        The request to update a Tax Rate is valid if:
        - The Tax Rate belongs to the requesting User's address
        """
        # The Tax Rate belongs to the requesting User's address
        if request.user.address['id'] != obj.address_id:
            return Http403(error_code='financial_tax_rate_update_201')

        return None

    @staticmethod
    def delete(request: Request, obj: TaxRate) -> Optional[Http403]:
        """
        The request to delete a Tax Rate is valid if:
        - The Tax Rate belongs to the requesting User's Address
        - The Tax Rate is not the last Tax Rate record for the Address
        """
        # The Tax Rate belongs to the requesting User's Address
        if request.user.address['id'] != obj.address_id:
            return Http403(error_code='financial_tax_rate_delete_201')

        # The Tax Rate is not the last Tax Rate record for the Address
        if TaxRate.objects.filter(
            address_id=request.user.address['id'],
        ).count() == 1:
            return Http403(error_code='financial_tax_rate_delete_202')

        return None
