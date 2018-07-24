import ckan.plugins as p
from ckanext.gallery.plugins.interfaces import IGalleryImage


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
        Get images from field value and returns them as a list of dicts specifying just the href.

        :param field_value: the value of the record's image field
        :param record: the record dict itself
        :param data_dict: relevant data in a dict, currently we only use the resource_view contained within
        :return: a list of dicts
        """
        # retrieve the delimiter if there is one
        delimiter = data_dict['resource_view'].get('image_delimiter', None)
        if delimiter:
            # split the text by the delimiter if we have one
            images = field_value.split(delimiter)
        else:
            images = [field_value]

        return [{'href': image.strip()} for image in images if image.strip()]
