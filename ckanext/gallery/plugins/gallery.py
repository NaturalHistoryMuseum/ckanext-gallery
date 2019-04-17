#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-gallery
# Created by the Natural History Museum in London, UK

import copy
import urllib

from ckanext.gallery.lib.helpers import get_datastore_fields
from ckanext.gallery.logic.validators import is_datastore_field
from ckanext.gallery.plugins.interfaces import IGalleryImage

from ckan.plugins import (PluginImplementations, SingletonPlugin, get_plugin, implements,
                          interfaces, toolkit)
from ckan.lib import helpers  # helpers.Page is not in toolkit.h
from ckanext.datastore.interfaces import IDatastore

not_empty = toolkit.get_validator(u'not_empty')
ignore_empty = toolkit.get_validator(u'ignore_empty')

IS_NOT_NULL = u'IS NOT NULL'


class GalleryPlugin(SingletonPlugin):
    '''Gallery plugin'''
    implements(interfaces.IConfigurer)
    implements(interfaces.IResourceView, inherit=True)
    implements(IDatastore, inherit=True)

    ## IConfigurer
    def update_config(self, config):
        '''Add our template directories to the list of available templates

        :param config: 

        '''
        toolkit.add_template_directory(config, u'../theme/templates')
        toolkit.add_public_directory(config, u'../theme/public')
        toolkit.add_resource(u'../theme/public', u'ckanext-gallery')

    ## IResourceView
    def info(self):
        ''' '''
        return {
            u'name': u'gallery',
            u'title': u'Gallery',
            u'schema': {
                u'image_field': [not_empty, is_datastore_field],
                u'image_plugin': [not_empty],
                u'image_title': [ignore_empty, is_datastore_field],
                u'image_delimiter': [ignore_empty],
                },
            u'icon': u'image',
            u'iframed': False,
            u'filterable': True,
            u'preview_enabled': False,
            u'full_page_edit': False
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
        return u'gallery/view.html'

    def form_template(self, context, data_dict):
        '''

        :param context: 
        :param data_dict: 

        '''
        return u'gallery/form.html'

    def can_view(self, data_dict):
        '''Specify which resources can be viewed by this plugin

        :param data_dict: 

        '''
        # Check that we have a datastore for this resource
        if data_dict[u'resource'].get(u'datastore_active'):
            return True
        return False

    def _get_request_filters(self):
        ''' '''
        filters = {}
        for f in urllib.unquote(toolkit.request.params.get(u'filters', u'')).split(u'|'):
            if f:
                (k, v) = f.split(u':', 1)
                if k not in filters:
                    filters[k] = []
                filters[k].append(v)
        return filters

    def setup_template_variables(self, context, data_dict):
        '''Setup variables available to templates

        :param context: 
        :param data_dict: 

        '''

        records_per_page = toolkit.config.get(u'ckanext.gallery.records_per_page', 32)
        current_page = toolkit.request.params.get(u'page', 1)
        image_list = []

        # Get list of datastore fields and format into a dict, ready for a form
        datastore_fields = get_datastore_fields(data_dict[u'resource'][u'id'])

        image_plugins = []
        # Get gallery image plugins
        for plugin in PluginImplementations(IGalleryImage):
            image_info = plugin.image_info()
            # If we have resource type set, make sure the format of the resource matches
            # Otherwise continue to next record
            if image_info[u'resource_type'] and data_dict[u'resource'][
                u'format'].lower() not in image_info[u'resource_type']:
                continue
            image_info[u'plugin'] = plugin
            image_plugins.append(image_info)

        image_field = data_dict[u'resource_view'].get(u'image_field', None)
        image_plugin = data_dict[u'resource_view'].get(u'image_plugin', None)
        image_title_field = data_dict[u'resource_view'].get(u'image_title', None)
        # Set up template variables
        tpl_variables = {
            u'images': image_list,
            u'datastore_fields': [{
                u'value': f[u'id'],
                u'text': f[u'id']
                } for f in datastore_fields],
            u'image_plugins': [{
                u'value': f[u'plugin'].name,
                u'text': f[u'title']
                } for f in image_plugins],
            u'defaults': {},
            u'resource_id': data_dict[u'resource'][u'id'],
            u'package_name': data_dict[u'package'][u'name']
            }
        # Load the images
        # Only try and load images, if an image field has been selected
        if image_field and image_plugin:
            offset = (int(current_page) - 1) * records_per_page
            # We only want to get records that have both the image field populated
            # So add filters to the datastore search params
            filters = self._get_request_filters()
            # TODO: copy across to NHM code that handles this
            if data_dict[u'resource'][u'format'].lower() == u'dwc':
                filters[u'_has_image'] = u'true'

            params = {
                u'resource_id': data_dict[u'resource'][u'id'],
                u'limit': records_per_page,
                u'offset': offset,
                u'filters': filters,
                u'sort': u'_id'
                }
            # Add the full text filter
            fulltext = toolkit.request.params.get(u'q')
            if fulltext:
                params[u'q'] = fulltext
            # Try and use the solr search if it exists
            search_action = toolkit.get_action(u'datastore_search')
            # Perform the actual search
            data = search_action({}, params)
            item_count = data.get(u'total', 0)
            # Get the selected gallery image plugin
            plugin = get_plugin(image_plugin)
            if plugin:
                for record in data[u'records']:
                    image_title = record.get(image_title_field, u'')
                    image_defaults = {
                        u'title': image_title,
                        u'record_id': record[u'_id'],
                        u'resource_id': data_dict[u'resource'][u'id']
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
                u'collection': data[u'records'],
                u'page': current_page,
                u'url': self.pager_url,
                u'items_per_page': records_per_page,
                u'item_count': item_count,
                }
            # Add filter params to page links
            for key in [u'q', u'filters']:
                value = toolkit.request.params.get(key)
                if value:
                    page_params[key] = value

            tpl_variables[u'page'] = helpers.Page(**page_params)

        return tpl_variables

    def pager_url(self, **kwargs):
        '''Adds a view id to the kwargs passed to the ckan pager_url function.

        '''
        view_id = toolkit.request.params.get(u'view_id')
        if view_id:
            kwargs[u'view_id'] = view_id
        return toolkit.h.pager_url(**kwargs)
