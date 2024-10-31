from mock import MagicMock, patch

from ckanext.gallery.lib import helpers


def test_get_datastore_fields():
    resource_id = MagicMock()
    mock_return = {'fields': MagicMock()}
    datastore_search_mock = MagicMock(return_value=mock_return)
    mock_toolkit = MagicMock(get_action=MagicMock(return_value=datastore_search_mock))

    with patch('ckanext.gallery.lib.helpers.toolkit', mock_toolkit):
        fields = helpers.get_datastore_fields(resource_id)

        assert fields == mock_return['fields']
        expected_data_dict = {'resource_id': resource_id, 'limit': 0}
        datastore_search_mock.assert_called_once_with({}, expected_data_dict)
        assert resource_id in helpers._cache
        assert fields == helpers._cache[resource_id]
        assert fields == helpers.get_datastore_fields(resource_id)
