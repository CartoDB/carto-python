"""
Entity classes for defining synchronizations

.. module:: carto.synchronizations
   :platform: Unix, Windows
   :synopsis: Entity classes for defining synchronizations

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

from pyrestcli.resources import Resource
from pyrestcli.fields import CharField, DateTimeField, BooleanField, IntegerField


class Synchronization(Resource):
    """
    Represents a synchronization in CARTO. This is an internal data type, with no
    specific API endpoints
    """
    checksum = CharField()
    created_at = DateTimeField()
    error_code = CharField()
    error_message = CharField()
    id = CharField()
    interval = IntegerField()
    modified_at = DateTimeField()
    name = CharField()
    ran_at = DateTimeField()
    retried_times = IntegerField()
    run_at = DateTimeField()
    service_item_id = CharField()
    service_name = CharField()
    state = CharField()
    updated_at = DateTimeField()
    url = CharField()
    user_id = CharField()
    content_guessing = BooleanField()
    etag = CharField()
    log_id = BooleanField()
    quoted_fields_guessing = BooleanField()
    type_guessing = BooleanField()
    from_external_source = BooleanField()
    visualization_id = BooleanField()
