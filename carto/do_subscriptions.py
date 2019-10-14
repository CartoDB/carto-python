# -*- coding: utf-8 -*-
"""
Module for working with Data Observatory Subscriptions

.. module:: carto.do_subscriptions
   :platform: Unix, Windows
   :synopsis: Module for working with Data Observatory Subscriptions

.. moduleauthor:: Jesús Arroyo <jarroyo@carto.com>


"""

from pyrestcli.fields import CharField, FloatField

from .resources import Resource, Manager
from .paginators import CartoPaginator


API_VERSION = "v4"
API_ENDPOINT = "api/{api_version}/do/subscriptions"


class DOSubscription(Resource):
    """
    Represents a Data Observatory Subscriptions in CARTO.

    """
    dataset = CharField()
    id = CharField()
    project = CharField()
    table = CharField()
    type = CharField()

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        name_field = "id"


class DOSubscriptionManager(Manager):
    """
    Manager for the DOSubscription class.

    """
    resource_class = DOSubscription
    json_collection_attribute = "subscriptions"
    paginator_class = CartoPaginator


class DOCreatedSubscription(Resource):
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


class DOSubscriptionCreationManager(Manager):
    """
    Manager for the DOSubscription class.

    """
    resource_class = DOCreatedSubscription
    json_collection_attribute = "subscriptions"
    paginator_class = CartoPaginator
