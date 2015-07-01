#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import ckan.plugins as p

_cache = {}

def get_datastore_fields(resource_id):
    """
    Retrieve list of dataset fields
    Checked between requests so we can quickly reuse without searching again
    :param resource_id:
    :return:
    """
    try:
        fields = _cache[resource_id]
    except KeyError:
        data = {'resource_id': resource_id, 'limit': 0}
        fields = _cache[resource_id] = p.toolkit.get_action('datastore_search')({}, data)['fields']
    return fields