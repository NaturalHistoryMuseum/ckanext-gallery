#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gallery
# Created by the Natural History Museum in London, UK

from ckan.plugins import interfaces


class IGalleryImage(interfaces.Interface):
    """
    IGallery plugin for retrieving images from records.
    """

    def image_info(self):
        """
        Returns information about this plugin.

        :return:
        """

    def get_images(self, field_value, record, data_dict):
        """
        Retrieve images from a record and present them as a list of dicts. Valid output
        fields for each image:

            - href (main/preview URL; required)
            - thumbnail (URL for a smaller version of the image)
            - download (URL for the downloadable version of the image)
            - link (e.g. record URL, displayed in popup viewer)
            - copyright (licence information; HTML)
            - description (displayed under the image thumbnail; HTML)
            - title (title in the popup viewer and image alt)
            - record_id

        :return: list of dicts
        """
