<!--header-start-->
<img src="https://github.com/NaturalHistoryMuseum/ckanext-gallery/raw/main/.github/nhm-logo.svg" align="left" width="150px" height="100px" hspace="40"/>

# ckanext-gallery

[![Tests](https://img.shields.io/github/actions/workflow/status/NaturalHistoryMuseum/ckanext-gallery/main.yml?style=flat-square)](https://github.com/NaturalHistoryMuseum/ckanext-gallery/actions/workflows/main.yml)
[![Coveralls](https://img.shields.io/coveralls/github/NaturalHistoryMuseum/ckanext-gallery/main?style=flat-square)](https://coveralls.io/github/NaturalHistoryMuseum/ckanext-gallery)
[![CKAN](https://img.shields.io/badge/ckan-2.9.7-orange.svg?style=flat-square)](https://github.com/ckan/ckan)
[![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue.svg?style=flat-square)](https://www.python.org/)
[![Docs](https://img.shields.io/readthedocs/ckanext-gallery?style=flat-square)](https://ckanext-gallery.readthedocs.io)

_A CKAN extension for a dataset gallery view._

<!--header-end-->

# Overview

<!--overview-start-->
Adds a gallery view for resources on a CKAN instance. Two plugins are included in this extension: `gallery` and `gallery_image`.

Based on [blueimp Gallery](https://blueimp.github.io/Gallery).

<!--overview-end-->

# Installation

<!--installation-start-->
Path variables used below:
- `$INSTALL_FOLDER` (i.e. where CKAN is installed), e.g. `/usr/lib/ckan/default`
- `$CONFIG_FILE`, e.g. `/etc/ckan/default/development.ini`

## Installing from PyPI

```shell
pip install ckanext-gallery
```

## Installing from source

1. Clone the repository into the `src` folder:
   ```shell
   cd $INSTALL_FOLDER/src
   git clone https://github.com/NaturalHistoryMuseum/ckanext-gallery.git
   ```

2. Activate the virtual env:
   ```shell
   . $INSTALL_FOLDER/bin/activate
   ```

3. Install via pip:
   ```shell
   pip install $INSTALL_FOLDER/src/ckanext-gallery
   ```

### Installing in editable mode

Installing from a `pyproject.toml` in editable mode (i.e. `pip install -e`) requires `setuptools>=64`; however, CKAN 2.9 requires `setuptools==44.1.0`. See [our CKAN fork](https://github.com/NaturalHistoryMuseum/ckan) for a version of v2.9 that uses an updated setuptools if this functionality is something you need.

## Post-install setup

1. Add 'gallery' to the list of plugins in your `$CONFIG_FILE`:
   ```ini
   ckan.plugins = ... gallery
   ```

2. Install `lessc` globally:
   ```shell
   npm install -g "less@~4.1"
   ```

<!--installation-end-->

# Configuration

<!--configuration-start-->
There's only one option that can be specified in the `.ini` file:

| Name                               | Description                           | Default |
|------------------------------------|---------------------------------------|---------|
| `ckanext.gallery.records_per_page` | Number of images to display on a page | 32      |

<!--configuration-end-->

# Usage

<!--usage-start-->
To use as a view, no further setup is needed; the 'Gallery' type should be available for resources
after installing the plugin.

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

<!--usage-end-->

# Testing

<!--testing-start-->
There is a Docker compose configuration available in this repository to make it easier to run tests. The ckan image uses the Dockerfile in the `docker/` folder.

To run the tests against ckan 2.9.x on Python3:

1. Build the required images:
   ```shell
   docker-compose build
   ```

2. Then run the tests.
   The root of the repository is mounted into the ckan container as a volume by the Docker compose
   configuration, so you should only need to rebuild the ckan image if you change the extension's
   dependencies.
   ```shell
   docker-compose run ckan
   ```

<!--testing-end-->
