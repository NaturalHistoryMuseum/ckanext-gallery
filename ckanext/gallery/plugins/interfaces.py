#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gallery
# Created by the Natural History Museum in London, UK

from ckan.plugins import interfaces


class IGalleryImage(interfaces.Interface):
    """
    IGallery plugin for displaying image field.

    Can be extended - eg basic image in the gallery plugin
    Or DwC image field in the NHM plugin
    """

    def info(self):
        '''
        :return: name, title, description
        '''

    def can_view(self, resource, field):
        """
        Can this plugin view.

        :param resource: param field:
        :param field:
        """

    def thumbnail(self):
        """
        Thumbnail representation of the image.

        :return:
        """

    def image(self):
        """
        Full size representation of the image.

        :return:
        """
