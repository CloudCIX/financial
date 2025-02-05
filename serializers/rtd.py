# libs
import serpy
# local
from financial.serializers.custom_fields import DecimalField


__all__ = [
    'RTDSerializer',
]


class RTDLineSerializer(serpy.DictSerializer):
    """
    id:
        description: The id of a Tax Rate
        type: integer
    percent:
        description: The percent of a Tax Rate
        type: string
        format: decimal
    description:
        description: The description of a Tax Rate
        type: string
    total:
        description: The amount of money charged at the specified Tax Rate
        type: string
        format: decimal
    """
    id = serpy.Field()
    percent = DecimalField()
    description = serpy.Field()
    total = DecimalField()


class RTDSerializer(serpy.Serializer):
    """
    sales:
        description: Value of goods sold for the year
        type: array
        items:
            type: object
            properties:
                id:
                    type: integer
                description:
                    type: string
                percent:
                    type: string
                    format: decimal
                total:
                    type: string
                    format: decimal
    eu_purchases:
        description: Value of acquisitions from the EU excluding Ireland
        type: array
        items:
            type: object
            properties:
                id:
                    type: integer
                description:
                    type: string
                percent:
                    type: string
                    format: decimal
                total:
                    type: string
                    format: decimal
    resale_purchases:
        description: Value of all purchases meant for resale
        type: array
        items:
            type: object
            properties:
                id:
                    type: integer
                description:
                    type: string
                percent:
                    type: string
                    format: decimal
                total:
                    type: string
                    format: decimal
    non_resale_purchases:
        description: Value of all purchases not meant for resale
        type: array
        items:
            type: object
            properties:
                id:
                    type: integer
                description:
                    type: string
                percent:
                    type: string
                    format: decimal
                total:
                    type: string
                    format: decimal
    """
    sales = serpy.MethodField()
    eu_purchases = serpy.MethodField()
    resale_purchases = serpy.MethodField()
    non_resale_purchases = serpy.MethodField()

    def get_sales(self, obj):
        return RTDLineSerializer(instance=obj['sales'], many=True).data

    def get_eu_purchases(self, obj):
        return RTDLineSerializer(instance=obj['eu_purchases'], many=True).data

    def get_resale_purchases(self, obj):
        return RTDLineSerializer(instance=obj['resale_purchases'], many=True).data

    def get_non_resale_purchases(self, obj):
        return RTDLineSerializer(instance=obj['non_resale_purchases'], many=True).data
