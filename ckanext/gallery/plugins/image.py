#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gallery
# Created by the Natural History Museum in London, UK

from ckanext.gallery.plugins.interfaces import IGalleryImage

from ckan.plugins import SingletonPlugin, implements


class GalleryImagePlugin(SingletonPlugin):
    '''Implements the basic image field
    The URL of an image is present in a text field

    '''
    implements(IGalleryImage)

    def image_info(self):
        '''

        :returns: If resource type is set, only dataset of that type will be available

        '''
        return {
            u'title': u'Text',
            u'resource_type': [u'csv', u'tsv'],
            u'field_type': [u'text']
        }

    def get_images(self, field_value, record, data_dict):
        '''Get images from field value and returns them as a list of dicts specifying just the href.

        :param field_value: the value of the record's image field
        :param record: the record dict itself
        :param data_dict: relevant data in a dict, currently we only use the resource_view contained within
        :return: a list of dicts

        '''
        # retrieve the delimiter if there is one
        delimiter = data_dict[u'resource_view'].get(u'image_delimiter', None)
        if delimiter:
            # split the text by the delimiter if we have one
            images = field_value.split(delimiter)
        else:
            images = [field_value]

        return [{u'href': image.strip()} for image in images if image.strip()]
