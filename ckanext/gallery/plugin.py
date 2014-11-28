import re
import ckan.plugins as p
from ckan.common import json
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckan.common import _, c
import ckan.lib.navl.dictization_functions as df
import ckan.logic as logic
from ckanext.datastore.interfaces import IDatastore
from pylons import config
import ckan.lib.helpers as h
from ckan.common import json, request, _, response
from pylons import url as _pylons_default_url

get_action = logic.get_action

not_empty = p.toolkit.get_validator('not_empty')
ignore_empty = p.toolkit.get_validator('ignore_empty')
Invalid = df.Invalid
Missing = df.Missing

IS_NOT_NULL = 'IS NOT NULL'

def in_list(list_possible_values):
    '''
    Validator that checks that the input value is one of the given
    possible values.

    :param list_possible_values: function that returns list of possible values
        for validated field
    :type possible_values: function
    '''
    def validate(key, data, errors, context):
        if not data[key] in list_possible_values():
            raise Invalid('"{0}" is not a valid parameter'.format(data[key]))
    return validate


def is_string_field(datastore_fields):
    '''
    Validator that checks that the selected field is a string

    :param list_possible_values: function that returns list of possible values
        for validated field
    :type possible_values: function
    '''
    def validate(key, data, errors, context):
        raise Invalid('"{0}" is not a string field'.format(data[key]))

    return validate


class GalleryPlugin(p.SingletonPlugin):
    """
    Gallery plugin
    """
    p.implements(p.IConfigurer)
    p.implements(p.IResourceView, inherit=True)
    p.implements(IDatastore, inherit=True)

    datastore_fields = []

    ## IConfigurer
    def update_config(self, config):
        """Add our template directories to the list of available templates"""
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_resource('theme/public', 'ckanext-gallery')

    ## IResourceView
    def info(self):
        """Return generic info about the plugin"""
        return {
            'name': 'gallery',
            'title': 'Gallery',
            'schema': {
                'image_field': [not_empty, in_list(self.list_datastore_fields), is_string_field(self.datastore_fields)],
                'thumbnail_field': [not_empty, in_list(self.list_datastore_fields)],
                'thumbnail_params': [],
                'gallery_title_field': [ignore_empty, in_list(self.list_datastore_fields)],
                'modal_title_field': [ignore_empty, in_list(self.list_datastore_fields)]
            },
            'icon': 'picture',
            'iframed': False,
            'filterable': True,
            'preview_enabled': False,
            'full_page_edit': False
        }

    # IDatastore
    def datastore_search(self, context, data_dict, all_field_ids, query_dict):

        clauses = []

        # First, make sure we don't have any of the 'IS NOT NONE' string filters in the where clause
        # We need to do this here, rather than in datastore_validate_query because the filters have already
        # been processed and removed
        query_dict['where'] = [where for where in query_dict['where'] if len(where) < 2 or where[1] != IS_NOT_NULL]

        # And then add SQL based where clauses
        try:
            for field_name, value in data_dict['filters'].items():
                if value == IS_NOT_NULL:
                    clauses.append(('"%s" %s' % (field_name, IS_NOT_NULL), ))
                    pass
                query_dict['where'] += clauses
        except KeyError:
            pass

        return query_dict

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

    def setup_template_variables(self, context, data_dict):
        """Setup variables available to templates"""

        self.datastore_fields = self._get_datastore_fields(data_dict['resource']['id'])

        field_separator = config.get("ckanext.gallery.field_separator", ';')
        records_per_page = config.get("ckanext.gallery.records_per_page", 30)

        current_page = request.params.get('page', 1)

        image_field = data_dict['resource_view'].get('image_field')
        gallery_title_field = data_dict['resource_view'].get('gallery_title_field', None)
        modal_title_field = data_dict['resource_view'].get('modal_title_field', None)

        thumbnail_params = data_dict['resource_view'].get('thumbnail_params', None)
        thumbnail_field = data_dict['resource_view'].get('thumbnail_field', None)

        image_list = []
        records = []
        item_count = 0

        # Only try and load images, if an image field has been selected
        if image_field:

            offset = (int(current_page) - 1) * records_per_page

            # We only want to get records that have both the image field populated
            # So add filters to the datastore search params
            params = {
                'resource_id': data_dict['resource']['id'],
                'limit': records_per_page,
                'offset': offset,
                'filters': {
                    image_field: IS_NOT_NULL
                }
            }

            # Add filters from request
            filter_str = request.params.get('filters')
            if filter_str:
                for f in filter_str.split('|'):
                    try:
                        (name, value) = f.split(':')
                        params['filters'][name] = value

                    except ValueError:
                        pass

            # Full text filter
            fulltext = request.params.get('q')
            if fulltext:
                params['q'] = fulltext

            context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
            data = toolkit.get_action('datastore_search')(context, params)

            item_count = data.get('total', 0)
            records = data['records']

            for record in data['records']:

                try:
                    images = record.get(image_field, None).split(field_separator)
                except AttributeError:
                    pass
                else:
                    # Only add if we have an image
                    if images:

                        gallery_title = record.get(gallery_title_field, None)
                        modal_title = record.get(modal_title_field, None)
                        thumbnails = record.get(thumbnail_field, None).split(field_separator)

                        for i, image in enumerate(images):

                            image = image.strip()

                            if thumbnails:
                                try:
                                    thumbnail = thumbnails[i]
                                except IndexError:
                                    # If we don't have a thumbnail with the same index
                                    # Use the first thumbnail image
                                    thumbnail = thumbnails[0]

                                thumbnail = thumbnail.strip()

                                # If we have thumbnail params, add them here
                                if thumbnail_params:
                                    q = '&' if '?' in thumbnail else '?'
                                    thumbnail += q + thumbnail_params

                            image_list.append({
                                'url': image,
                                'thumbnail': thumbnail,
                                'gallery_title': gallery_title,
                                'modal_title': modal_title,
                                'record_id': record['_id']
                            })

        page_params = {
            'collection':records,
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

        page = h.Page(**page_params)

        return {
            'images': image_list,
            'datastore_fields':  self.datastore_fields,
            'defaults': {},
            'resource_id': data_dict['resource']['id'],
            'package_name': data_dict['package']['name'],
            'page': page
        }

    def _get_datastore_fields(self, resource_id):
        data = {'resource_id': resource_id, 'limit': 0}
        fields = toolkit.get_action('datastore_search')({}, data)['fields']

        print fields

        return [{'value': f['id'], 'text': f['id']} for f in fields]

    def list_datastore_fields(self):
        return [t['value'] for t in self.datastore_fields]

    def pager_url(self, **kwargs):
        routes_dict = _pylons_default_url.environ['pylons.routes_dict']
        view_id = request.params.get('view_id')
        if view_id:
            routes_dict['view_id'] = view_id
        routes_dict.update(kwargs)
        return h.url_for(**routes_dict)