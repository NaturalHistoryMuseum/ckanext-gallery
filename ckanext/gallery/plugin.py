import re
import ckan.plugins as p
from ckan.common import json
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckan.common import _, c
import ckan.lib.navl.dictization_functions as df
import ckan.logic as logic
from ckanext.datastore.interfaces import IDatastore
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

class GalleryPlugin(p.SingletonPlugin):
    """
    Gallery plugin
    """
    p.implements(p.IConfigurer)
    p.implements(p.IResourceView, inherit=True)
    p.implements(IDatastore)

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
                'image_field': [not_empty, in_list(self.list_datastore_fields)],
                'thumbnail_field': [not_empty, in_list(self.list_datastore_fields)],
                'thumbnail_params': [],
                'title_field': [ignore_empty, in_list(self.list_datastore_fields)]
            },
            'icon': 'picture',
            'iframed': False,
            'preview_enabled': False,
            'full_page_edit': False
        }

    # IDatastore
    def datastore_search(self, context, data_dict, all_field_ids, query_dict):

        clauses = []

        # First, make sure we don't have any of the 'IS NOT NONE' string filters in the where clause
        # We need to do this here, rather than in datastore_validate_query because the filters have already
        # been processed and removed
        query_dict['where'] = [where for where in query_dict['where'] if where[1] != IS_NOT_NULL]

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

    def datastore_validate_query(self, context, data_dict, all_field_ids):
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

        # Get the actual data - there's no need to do this client side
        # TODO: Q params
        # TODO: Pagination

        image_field = data_dict['resource_view'].get('image_field')
        title_field = data_dict['resource_view'].get('title_field', None)
        thumbnail_params = title_field = data_dict['resource_view'].get('title_field', None)
        thumbnail_field = data_dict['resource_view'].get('thumbnail_field')

        # We only want to get records that have both the image and thumbnail field populated
        # So add filters to the datastore search params
        params = {
            'resource_id': data_dict['resource']['id'],
            'limit': 100,
            'offset': 0,
            # TODO: This isn't working
            # 'filters': {
            #     image_field: IS_NOT_NULL,
            #     thumbnail_field: IS_NOT_NULL
            # }
        }

        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
        data = toolkit.get_action('datastore_search')(context, params)

        #  Build a list of images
        images = []
        for record in data['records']:

            image = record.get(image_field, None)

            # Only add if we have an image
            if image:

                title = record.get(title_field, None)
                thumbnail = record.get(thumbnail_field, None)

                # If we have thumbnail params, add them here
                thumbnail_params = record.get(thumbnail_field, None)
                if thumbnail and thumbnail_params:
                    q = '&' if '?' in thumbnail else '?'
                    thumbnail += q + thumbnail_params

                images.append({
                    'url': image,
                    'thumbnail': thumbnail,
                    'title': title
                })

        return {
            'images': images,
            'datastore_fields':  self.datastore_fields,
            'defaults': {}
        }

    def _get_datastore_fields(self, resource_id):
        data = {'resource_id': resource_id, 'limit': 0}
        fields = toolkit.get_action('datastore_search')({}, data)['fields']
        return [{'value': f['id'], 'text': f['id']} for f in fields]

    def list_datastore_fields(self):
        return [t['value'] for t in self.datastore_fields]