# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gallery
# Created by the Natural History Museum in London, UK

from ckanext.gallery.lib.helpers import get_datastore_fields

from ckan.plugins import toolkit


def is_datastore_field(value, context):
    """
    Make sure this field is an actual datastore field.

    :param value: list of field names
    :param context: the validation context
    :raises: toolkit.Invalid if the field is not in the resource's datastore
    :return: the value if it's valid
    """
    fields = get_datastore_fields(toolkit.c.resource.get('id'))
    for field in fields:
        if field['id'] in value:
            return value
    raise toolkit.Invalid(toolkit._('Field {0} not in datastore'.format(value)))
