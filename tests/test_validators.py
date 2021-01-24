import pytest
from ckan.plugins import toolkit
from ckanext.gallery.logic.validators import is_datastore_field
from mock import patch, MagicMock


class TestIsDatastoreField(object):

    def test_valid(self):
        test_field = u'beans'
        mock_fields = [
            {u'id': MagicMock()},
            {u'id': test_field},
            {u'id': MagicMock()},
        ]
        mock_toolkit = MagicMock()
        get_fields_mock = MagicMock(return_value=mock_fields)

        with patch(u'ckanext.gallery.logic.validators.toolkit', mock_toolkit):
            with patch(u'ckanext.gallery.logic.validators.get_datastore_fields', get_fields_mock):
                assert is_datastore_field([test_field], MagicMock()) == [test_field]

    def test_invalid(self):
        test_field = u'beans'
        mock_fields = [
            {u'id': MagicMock()},
            {u'id': MagicMock()},
            {u'id': MagicMock()},
        ]
        # we want to mock c but leave the other bits this function uses
        mock_toolkit = MagicMock(Invalid=toolkit.Invalid, _=toolkit._)
        get_fields_mock = MagicMock(return_value=mock_fields)

        with patch(u'ckanext.gallery.logic.validators.toolkit', mock_toolkit):
            with patch(u'ckanext.gallery.logic.validators.get_datastore_fields', get_fields_mock):
                with pytest.raises(toolkit.Invalid):
                    is_datastore_field([test_field], MagicMock())
