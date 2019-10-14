# -*- coding: utf-8 -*-
"""
Module for working with Data Observatory Subscription Information

.. module:: carto.do_subscription_info
   :platform: Unix, Windows
   :synopsis: Module for working with Data Observatory Subscription Information

.. moduleauthor:: Javier Goizueta <jgoizueta@carto.com>


"""

from pyrestcli.fields import CharField, FloatField

from .resources import Resource, Manager
from .paginators import CartoPaginator


API_VERSION = "v4"
API_ENDPOINT = "api/{api_version}/do/subscription_info"


class DOSubscriptionInfo(Resource):
    """
    Represents a Data Observatory Subscriptions in CARTO.

    """
    id = CharField()
    estimated_delivery_days = FloatField()
    subscription_list_price = FloatField()
    tos = CharField()
    tos_link = CharField()
    licenses = CharField()
    licenses_link = CharField()
    rights = CharField()
    type = CharField()

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        name_field = "id"


class DOSubscriptionInfoManager(Manager):
    """
    Manager for the DOSubscriptionInfo class.

    """
    resource_class = DOSubscriptionInfo
    json_collection_attribute = "subscription_info"
    paginator_class = CartoPaginator

    def get(self, id, type):
        response = self.send(self.get_collection_endpoint(), "get", params={"id": id, "type": type})

        try:
            resource = self.resource_class(self.client)
        except (ValueError, TypeError):
            return None
        else:
            response_data = self.client.get_response_data(response, self.Meta.parse_json)
        if response_data:
            resource.update_from_dict(response_data)
        return resource
