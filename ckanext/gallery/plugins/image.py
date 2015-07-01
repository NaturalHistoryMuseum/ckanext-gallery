import json
import ckan.plugins as p
import ckan.lib.helpers as h
from ckanext.gallery.plugins.interfaces import IGalleryImage
from webhelpers.html import literal

class GalleryImagePlugin(p.SingletonPlugin):
    """
    Implements the basic image field
    The URL of an image is present in a text field
    """
    p.implements(IGalleryImage)

    def image_info(self):
        """
        Return info for this plugin
        If resource type is set, only dataset of that type will be available
        :return:
        """
        return {
            'title': 'Text',
            'resource_type': ['csv'],
            'field_type': ['text']
        }

    def get_images(self, field_value, record, data_dict):
        """
        Get images from field
        :param field_value:
        :param record:
        :param data_dict:
        :return:
        """

        # Field value just contains the URL
        return [
            {
                'url': field_value
            }
        ]

