#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gallery
# Created by the Natural History Museum in London, UK

import json
import ckan.plugins as p
import ckan.lib.helpers as h
from ckanext.gallery.plugins.interfaces import IGalleryImage
from webhelpers.html import literal

class GalleryImagePlugin(p.SingletonPlugin):
    '''Implements the basic image field
    The URL of an image is present in a text field


    '''
    p.implements(IGalleryImage)

    def image_info(self):
        '''


        :returns: If resource type is set, only dataset of that type will be available
        :return:

        '''
        return {
            u'title': u'Text',
            u'resource_type': [u'csv'],
            u'field_type': [u'text']
        }

    def get_images(self, field_value, record, data_dict):
        '''Get images from field

        :param field_value: param record:
        :param data_dict: return:
        :param record: 

        '''

        # Field value just contains the URL
        return [
            {
                u'href': field_value
            }
        ]

