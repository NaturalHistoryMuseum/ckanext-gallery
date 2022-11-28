#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gallery
# Created by the Natural History Museum in London, UK

import copy

from ckan.lib import helpers  # helpers.Page is not in toolkit.h
from ckan.plugins import (
    PluginImplementations,
    SingletonPlugin,
    get_plugin,
    implements,
    interfaces,
    toolkit,
)
from ckanext.datastore.interfaces import IDatastore
from ckanext.gallery.lib.helpers import get_datastore_fields
from ckanext.gallery.logic.validators import is_datastore_field
from ckanext.gallery.plugins.interfaces import IGalleryImage
from urllib.parse import unquote

not_empty = toolkit.get_validator('not_empty')
ignore_empty = toolkit.get_validator('ignore_empty')

IS_NOT_NULL = 'IS NOT NULL'


class GalleryPlugin(SingletonPlugin):
    """
    Gallery plugin.
    """

    implements(interfaces.IConfigurer)
    implements(interfaces.IResourceView, inherit=True)
    implements(IDatastore, inherit=True)

    ## IConfigurer
    def update_config(self, config):
        """
        Add our template directories to the list of available templates.

        :param config:
        """
        toolkit.add_template_directory(config, '../theme/templates')
        toolkit.add_resource('../theme/assets', 'ckanext-gallery')
        toolkit.add_public_directory(config, '../theme/assets/vendor')

    ## IResourceView
    def info(self):
        return {
            'name': 'gallery',
            'title': 'Gallery',
            'schema': {
                'image_field': [not_empty, is_datastore_field],
                'image_plugin': [not_empty],
                'image_title': [ignore_empty, is_datastore_field],
                'image_delimiter': [ignore_empty],
            },
            'icon': 'image',
            'iframed': False,
            'filterable': True,
            'preview_enabled': False,
            'full_page_edit': False,
        }

    def datastore_validate(self, context, data_dict, all_field_ids):
        '''

        :param context:
        :param data_dict:
        :param all_field_ids:

        '''
        return data_dict

    def view_template(self, context, data_dict):
        '''

        :param context:
        :param data_dict:

        '''
        return 'gallery/view.html'

    def form_template(self, context, data_dict):
        '''

        :param context:
        :param data_dict:

        '''
        return 'gallery/form.html'

    def can_view(self, data_dict):
        """
        Specify which resources can be viewed by this plugin.

        :param data_dict:
        """
        # Check that we have a datastore for this resource
        if data_dict['resource'].get('datastore_active'):
            return True
        return False

    def _get_request_filters(self):
        filters = {}
        for f in unquote(toolkit.request.params.get('filters', '')).split('|'):
            if f:
                k, v = f.split(':', 1)
                if k not in filters:
                    filters[k] = []
                filters[k].append(v)
        return filters

    def setup_template_variables(self, context, data_dict):
        """
        Setup variables available to templates.

        :param context:
        :param data_dict:
        """
        records_per_page = toolkit.config.get('ckanext.gallery.records_per_page', 32)
        current_page = toolkit.request.params.get('page', 1)
        image_list = []

        # Get list of datastore fields and format into a dict, ready for a form
        datastore_fields = get_datastore_fields(data_dict['resource']['id'])

        image_plugins = []
        # Get gallery image plugins
        for plugin in PluginImplementations(IGalleryImage):
            image_info = plugin.image_info()
            # If we have resource type set, make sure the format of the resource matches
            # Otherwise continue to next record
            if (
                image_info['resource_type']
                and data_dict['resource']['format'].lower()
                not in image_info['resource_type']
            ):
                continue
            image_info['plugin'] = plugin
            image_plugins.append(image_info)

        image_field = data_dict['resource_view'].get('image_field', None)
        image_plugin = data_dict['resource_view'].get('image_plugin', None)
        image_title_field = data_dict['resource_view'].get('image_title', None)
        # Set up template variables
        tpl_variables = {
            'images': image_list,
            'datastore_fields': [
                {'value': f['id'], 'text': f['id']} for f in datastore_fields
            ],
            'image_plugins': [
                {'value': f['plugin'].name, 'text': f['title']} for f in image_plugins
            ],
            'defaults': {},
            'resource_id': data_dict['resource']['id'],
            'package_name': data_dict['package']['name'],
        }
        # Load the images
        # Only try and load images, if an image field has been selected
        if image_field and image_plugin:
            offset = (int(current_page) - 1) * records_per_page
            # We only want to get records that have both the image field populated
            # So add filters to the datastore search params
            filters = self._get_request_filters()
            # TODO: copy across to NHM code that handles this
            if data_dict['resource']['format'].lower() == 'dwc':
                filters['_has_image'] = 'true'

            params = {
                'resource_id': data_dict['resource']['id'],
                'limit': records_per_page,
                'offset': offset,
                'filters': filters,
                'sort': '_id',
            }
            # Add the full text filter
            fulltext = toolkit.request.params.get('q')
            if fulltext:
                params['q'] = fulltext
            # Try and use the solr search if it exists
            search_action = toolkit.get_action('datastore_search')
            # Perform the actual search
            data = search_action({}, params)
            item_count = data.get('total', 0)
            # Get the selected gallery image plugin
            plugin = get_plugin(image_plugin)
            if plugin:
                for record in data['records']:
                    image_title = record.get(image_title_field, '')
                    image_defaults = {
                        'title': image_title,
                        'record_id': record['_id'],
                        'resource_id': data_dict['resource']['id'],
                    }
                    field_value = record.get(image_field, None)
                    if field_value:
                        images = plugin.get_images(field_value, record, data_dict)
                        for image in images:
                            image_default_copy = copy.copy(image_defaults)
                            # Merge in the plugin image settings to the default image
                            # Using an copy so the defaults do not change for multiple
                            #  images
                            image_default_copy.update(image)
                            image_list.append(image_default_copy)

            page_params = {
                'collection': data['records'],
                'page': current_page,
                'url': self.pager_url,
                'items_per_page': records_per_page,
                'item_count': item_count,
            }
            # Add filter params to page links
            for key in ['q', 'filters']:
                value = toolkit.request.params.get(key)
                if value:
                    page_params[key] = value

            tpl_variables['page'] = helpers.Page(**page_params)

        return tpl_variables

    def pager_url(self, **kwargs):
        """
        Adds a view id and the view args to the kwargs passed to the ckan pager_url
        function.
        """
        view_id = toolkit.request.params.get('view_id')
        if view_id:
            kwargs['view_id'] = str(view_id)
        kwargs.update(toolkit.request.view_args)
        return toolkit.h.pager_url(**kwargs)
