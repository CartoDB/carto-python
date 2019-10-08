# -*- coding: utf-8 -*-
"""
Module for working with Data Observatory Datasets

.. module:: carto.do_datasets
   :platform: Unix, Windows
   :synopsis: Module for working with Data Observatory Datasets

.. moduleauthor:: Jesús Arroyo <jarroyo@carto.com>


"""

from pyrestcli.fields import CharField

from .resources import Resource, Manager
from .paginators import CartoPaginator


API_VERSION = "v4"
API_ENDPOINT = "api/{api_version}/do/datasets"


class DODataset(Resource):
    """
    Represents a Data Observatory Datasets object in CARTO.

    """
    dataset = CharField()
    id = CharField()
    project = CharField()
    table = CharField()

    class Meta:
            collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
            name_field = "id"


class DODatasetManager(Manager):
    """
    Manager for the DODataset class.

    """
    resource_class = DODataset
    json_collection_attribute = "datasets"
    paginator_class = CartoPaginator
