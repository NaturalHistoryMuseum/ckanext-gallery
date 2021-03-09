from ckanext.gallery.lib import helpers
from mock import patch, MagicMock


def test_get_datastore_fields():
    resource_id = MagicMock()
    mock_return = {
        u'fields': MagicMock()
    }
    datastore_search_mock = MagicMock(return_value=mock_return)
    mock_toolkit = MagicMock(get_action=MagicMock(return_value=datastore_search_mock))

    with patch(u'ckanext.gallery.lib.helpers.toolkit', mock_toolkit):
        fields = helpers.get_datastore_fields(resource_id)

        assert fields == mock_return[u'fields']
        expected_data_dict = {
            u'resource_id': resource_id,
            u'limit': 0
        }
        datastore_search_mock.assert_called_once_with({}, expected_data_dict)
        assert resource_id in helpers._cache
        assert fields == helpers._cache[resource_id]
        assert fields == helpers.get_datastore_fields(resource_id)
