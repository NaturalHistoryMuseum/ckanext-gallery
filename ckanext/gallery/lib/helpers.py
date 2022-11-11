# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gallery
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit

_cache = {}


def get_datastore_fields(resource_id):
    """
    Retrieve list of dataset fields Checked between requests so we can quickly reuse
    without searching again.

    :param resource_id: return:
    :return: list of field dicts
    """
    try:
        fields = _cache[resource_id]
    except KeyError:
        data = {'resource_id': resource_id, 'limit': 0}
        fields = _cache[resource_id] = toolkit.get_action('datastore_search')({}, data)[
            'fields'
        ]
    return fields
