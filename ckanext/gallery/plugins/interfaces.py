import ckan.plugins.interfaces as interfaces

class IGalleryImage(interfaces.Interface):
    """
    IGallery plugin for displaying image field
    Can be extended - eg basic image in the gallery plugin
    Or DwC image field in the NHM plugin
    """
    def info(self):
        """
        Return information on the plugin -
            name, title, description
        :return:
        """

    def can_view(self, resource, field):
        """
        Can this plugin view
        :param resource:
        :param field:
        :return:
        """

    def thumbnail(self):
        """
        Thumbnail representation of the image
        :return:
        """

    def image(self):
        """
        Full size representation of the image
        :return:
        """