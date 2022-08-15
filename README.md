<img src=".github/nhm-logo.svg" align="left" width="150px" height="100px" hspace="40"/>

# ckanext-gallery

[![Tests](https://github.com/NaturalHistoryMuseum/ckanext-gallery/actions/workflows/main.yml/badge.svg)](https://github.com/NaturalHistoryMuseum/ckanext-gallery/actions/workflows/main.yml)
[![Coveralls](https://img.shields.io/coveralls/github/NaturalHistoryMuseum/ckanext-gallery/master.svg?style=flat-square)](https://coveralls.io/github/NaturalHistoryMuseum/ckanext-gallery)
[![CKAN](https://img.shields.io/badge/ckan-2.9.1-orange.svg?style=flat-square)](https://github.com/ckan/ckan)
[![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue.svg?style=flat-square)](https://www.python.org/)

_A CKAN extension for a dataset gallery view._


# Overview

Adds a gallery view for resources on a CKAN instance. Two plugins are included in this extension: `gallery` and `gallery_image`.

Based on [blueimp Gallery](https://blueimp.github.io/Gallery).


# Installation

Path variables used below:
- `$INSTALL_FOLDER` (i.e. where CKAN is installed), e.g. `/usr/lib/ckan/default`
- `$CONFIG_FILE`, e.g. `/etc/ckan/default/development.ini`

1. Clone the repository into the `src` folder:

  ```bash
  cd $INSTALL_FOLDER/src
  git clone https://github.com/NaturalHistoryMuseum/ckanext-gallery.git
  ```

2. Activate the virtual env:

  ```bash
  . $INSTALL_FOLDER/bin/activate
  ```

3. Install the requirements from requirements.txt:

  ```bash
  cd $INSTALL_FOLDER/src/ckanext-gallery
  pip install -r requirements.txt
  ```

4. Run setup.py:

  ```bash
  cd $INSTALL_FOLDER/src/ckanext-gallery
  python setup.py develop
  ```

5. Add 'gallery' to the list of plugins in your `$CONFIG_FILE`:

  ```ini
  ckan.plugins = ... gallery
  ```

# Configuration

There's only one option that can be specified in the `.ini` file:

Name|Description|Default
--|---|--
`ckanext.gallery.records_per_page`|Number of images to display on a page|32


# Usage

To use as a view, the 'Gallery' type should be available after installing the plugin.

## Interfaces

The `IGalleryImage` interface allows plugins to override settings.

```python
from ckan.plugins import SingletonPlugin, implements
from ckanext.gallery.plugins.interfaces import IGalleryImage

class YourPlugin(SingletonPlugin):
  implements(IGalleryImage)


  def image_info(self):
    '''
    Return info for this plugin. If resource type is set,
    only datasets of that type will be available.
    '''
    return {u'title': u'Text',
            u'resource_type': [u'csv', u'tsv'],
            u'field_type': [u'text']}


  def get_images(self, field_value, record, data_dict):
    '''
    Process images from a single record to return custom metadata.
    The field_value depends on the image field you choose.
    '''
    images = [{
      u'href': field_value[u'url'],
      u'thumbnail': field_value[u'url'].replace(u'preview', u'thumbnail'),
      u'record_id': record[u'_id']
    } for img in field_value]
    return image
```

## Templates

### Gallery block snippet
```html+jinja
{% snippet 'gallery/snippets/gallery.html', images=g.images, resource_id=res.id %}
```


# Testing
_Test coverage is currently extremely limited._

To run the tests in this extension, there is a Docker compose configuration available in this
repository to make it easy.

To run the tests against ckan 2.9.x on Python3:

1. Build the required images
```bash
docker-compose build
```

2. Then run the tests.
   The root of the repository is mounted into the ckan container as a volume by the Docker compose
   configuration, so you should only need to rebuild the ckan image if you change the extension's
   dependencies.
```bash
docker-compose run ckan
```

The ckan image uses the Dockerfile in the `docker/` folder which is based on `openknowledge/ckan-dev:2.9`.
