
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gallery
# Created by the Natural History Museum in London, UK

import ckan.plugins as p
from ckan.common import _

from ckanext.gallery.lib.helpers import get_datastore_fields

Invalid = p.toolkit.Invalid


def is_datastore_field(value, context):
    '''Make sure this field is an actual datastore field

    :param value: 
    :param context: 

    '''
    fields = get_datastore_fields(context[u'resource'].id)
    for field in fields:
        if field[u'id'] in value:
            return value
    raise Invalid(_(u'Field {0} not in datastore'.format(value)))

