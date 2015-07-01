#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import ckan.plugins as p
from ckan.common import _

from ckanext.gallery.lib.helpers import get_datastore_fields

Invalid = p.toolkit.Invalid


def is_datastore_field(value, context):
    '''
    Make sure this field is an actual datastore field

    :raises: ckan.lib.navl.dictization_functions.Invalid for other
        inputs or non-whole values
    '''
    fields = get_datastore_fields(context['resource'].id)
    for field in fields:
        if field['id'] in value:
            return value
    raise Invalid(_('Field {0} not in datastore'.format(value)))


def is_image_field():
    '''



    :param list_possible_values: function that returns list of possible values
        for validated field
    :type possible_values: function
    '''
    def validate(key, data, errors, context):

        # print key
        # print data

        # for f in context:
        #
        #
        # print context

        # print data[key]

        # print datastore_fields



        raise Invalid('"{0}" is not a string field'.format(data[key]))

    return validate
