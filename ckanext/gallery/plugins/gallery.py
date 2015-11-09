import copy
import urllib
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckan.common import _, c
import ckan.lib.navl.dictization_functions as df
import ckan.logic as logic
from ckanext.datastore.interfaces import IDatastore
from pylons import config
import ckan.lib.helpers as h
from ckan.common import request
from pylons import url as _pylons_default_url

from ckanext.gallery.logic.validators import is_datastore_field
from ckanext.gallery.plugins.interfaces import IGalleryImage
from ckanext.gallery.lib.helpers import get_datastore_fields


get_action = logic.get_action

not_empty = p.toolkit.get_validator('not_empty')
ignore_empty = p.toolkit.get_validator('ignore_empty')
Invalid = df.Invalid
Missing = df.Missing

IS_NOT_NULL = 'IS NOT NULL'

class GalleryPlugin(p.SingletonPlugin):
    """
    Gallery plugin
    """
    p.implements(p.IConfigurer)
    p.implements(p.IResourceView, inherit=True)
    p.implements(IDatastore, inherit=True)

    ## IConfigurer
    def update_config(self, config):
        """Add our template directories to the list of available templates"""
        p.toolkit.add_template_directory(config, '../theme/templates')
        p.toolkit.add_public_directory(config, '../theme/public')
        p.toolkit.add_resource('../theme/public', 'ckanext-gallery')

    ## IResourceView
    def info(self):
        """Return generic info about the plugin"""
        return {
            'name': 'gallery',
            'title': 'Gallery',
            'schema': {
                'image_field': [not_empty, is_datastore_field],
                'image_plugin': [not_empty],
                'image_title': [ignore_empty, is_datastore_field]
            },
            'icon': 'picture',
            'iframed': False,
            'filterable': True,
            'preview_enabled': False,
            'full_page_edit': False
        }

    def datastore_validate(self, context, data_dict, all_field_ids):
        return data_dict

    def view_template(self, context, data_dict):
        return 'gallery/view.html'

    def form_template(self, context, data_dict):
        return 'gallery/form.html'

    def can_view(self, data_dict):
        """Specify which resources can be viewed by this plugin"""
        # Check that we have a datastore for this resource
        if data_dict['resource'].get('datastore_active'):
            return True
        return False

    def _get_request_filters(self):
        """Return a dict representing the filters of the current request"""
        filters = {}
        for f in urllib.unquote(request.params.get('filters', '')).split('|'):
            if f:
                (k, v) = f.split(':', 1)
                if k not in filters:
                    filters[k] = []
                filters[k].append(v)
        return filters

    def setup_template_variables(self, context, data_dict):
        """Setup variables available to templates"""

        records_per_page = config.get("ckanext.gallery.records_per_page", 32)
        current_page = request.params.get('page', 1)
        image_list = []

        # Get list of datastore fields and format into a dict, ready for a form
        datastore_fields = get_datastore_fields(data_dict['resource']['id'])

        image_plugins = []
        # Get gallery image plugins
        for plugin in p.PluginImplementations(IGalleryImage):
            image_info = plugin.image_info()
            # If we have resource type set, make sure the format of the resource matches
            # Otherwise continue to next record
            if image_info['resource_type'] and data_dict['resource']['format'].lower() not in image_info['resource_type']:
                continue
            image_info['plugin'] = plugin
            image_plugins.append(image_info)

        image_field = data_dict['resource_view'].get('image_field', None)
        image_plugin = data_dict['resource_view'].get('image_plugin', None)
        image_title_field = data_dict['resource_view'].get('image_title', None)
        # Set up template variables
        tpl_variables = {
            'images': image_list,
            'datastore_fields': [{'value': f['id'], 'text': f['id']} for f in datastore_fields],
            'image_plugins': [{'value': f['plugin'].name, 'text': f['title']} for f in image_plugins],
            'defaults': {},
            'resource_id': data_dict['resource']['id'],
            'package_name': data_dict['package']['name']
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
                filters['_has_image'] = ['true']

            params = {
                'resource_id': data_dict['resource']['id'],
                'limit': records_per_page,
                'offset': offset,
                'filters': filters,
                'sort': '_id'
            }
            # Add the full text filter
            fulltext = request.params.get('q')
            if fulltext:
                params['q'] = fulltext
            # Try and use the solr search if it exists
            try:
                search_action = toolkit.get_action('datastore_solr_search')
            # Otherwise fallback to default
            except KeyError:
                search_action = toolkit.get_action('datastore_search')
            # Perform the actual search
            context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
            data = search_action(context, params)
            item_count = data.get('total', 0)
            # Get the selected gallery image plugin
            plugin = p.get_plugin(image_plugin)
            if plugin:
                for record in data['records']:
                    image_title = record.get(image_title_field, "")
                    image_defaults = {
                        'title': image_title,
                        'record_id': record['_id'],
                    }
                    field_value = record.get(image_field, None)
                    if field_value:
                        images = plugin.get_images(field_value, record, data_dict)
                        for image in images:
                            image_default_copy = copy.copy(image_defaults)
                            # Merge in the plugin image settings to the default image
                            # Using an copy so the defaults do not change for multiple images
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
                value = request.params.get(key)
                if value:
                    page_params[key] = value

            tpl_variables['page'] = h.Page(**page_params)

        return tpl_variables


    def pager_url(self, **kwargs):
        routes_dict = _pylons_default_url.environ['pylons.routes_dict']
        view_id = request.params.get('view_id')
        if view_id:
            routes_dict['view_id'] = view_id
        routes_dict.update(kwargs)
        return h.url_for(**routes_dict)
