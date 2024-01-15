#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gallery
# Created by the Natural History Museum in London, UK

from ckanext.gallery.plugins.interfaces import IGalleryImage

from ckan.plugins import SingletonPlugin, implements, toolkit


class GalleryIIIFPlugin(SingletonPlugin):
    """
    Implements the basic image field The URL of an image is present in a text field.
    """

    implements(IGalleryImage)

    def image_info(self):
        '''

        :returns: If resource type is set, only dataset of that type will be available

        '''
        return {
            'title': 'IIIF',
            'resource_type': ['csv', 'tsv'],
            'field_type': ['text'],
        }

    def get_images(self, field_value, record, data_dict):
        """
        Get images from field value and returns them as a list of dicts specifying just
        the href.

        :param field_value: the value of the record's image field
        :param record: the record dict itself
        :param data_dict: relevant data in a dict, currently we only use the resource_view contained within
        :return: a list of dicts
        """

        images = []

        # retrieve the delimiter if there is one
        delimiter = data_dict['resource_view'].get('image_delimiter', None)
        if delimiter:
            # split the text by the delimiter if we have one
            raw_images = field_value.split(delimiter)
        else:
            raw_images = [field_value]

        title_field = data_dict['resource_view'].get('image_title', None)

        for image in raw_images:
            title = record.get(title_field)
            image_base_url = image.strip().strip('/')

            if not image_base_url:
                continue

            images.append(
                {
                    'href': f'{image_base_url}',
                    'thumbnail': f'{image_base_url}/thumbnail',
                    'download': f'{image_base_url}/original',
                    'link': toolkit.url_for(
                        'record.view',
                        package_name=data_dict['package']['name'],
                        resource_id=data_dict['resource']['id'],
                        record_id=record['_id'],
                    ),
                    'description': title,
                    'title': title,
                    'record_id': record['_id'],
                }
            )

        return images
