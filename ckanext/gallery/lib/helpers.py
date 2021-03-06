# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gallery
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit

_cache = {}


def get_datastore_fields(resource_id):
    '''Retrieve list of dataset fields
    Checked between requests so we can quickly reuse without searching again

    :param resource_id: return:

    '''
    try:
        fields = _cache[resource_id]
    except KeyError:
        data = {
            u'resource_id': resource_id,
            u'limit': 0
            }
        fields = _cache[resource_id] = \
            toolkit.get_action(u'datastore_search')({}, data)[u'fields']
    return fields
