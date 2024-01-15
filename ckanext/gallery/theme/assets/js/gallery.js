ckan.module('gallery', function (jQuery, _) {
  var self;

  return {
    initialize: function () {
      self = this;
      $('a', this.el).each(function (i) {
        $(this).data('index', i);
        $(this).on('click', jQuery.proxy(self._openLightbox));
      });
    },
    getCurrentImage: function () {
      var pos = self.gallery.getIndex();
      return self.options.images[pos];
    },
    _openLightbox: function (e) {
      var options = {
        index: $(this).data('index'),
        onslide: function () {
          self._onImageUpdate();
        },
      };
      self.gallery = blueimp.Gallery(self.options.images, options);
      e.stopPropagation();
      return false;
    },
    _onImageUpdate: function () {
      var image = self.getCurrentImage();
      var $gallery = $('#blueimp-gallery');
      // Set image data attribute
      $gallery.data('image', image);

      // Update download link
      $('#blueimp-gallery a.gallery-control-download').attr(
        'href',
        image.download || image.href,
      );

      if (image.copyright) {
        $gallery.find('.copyright').html(image.copyright);
      }
      // If we have a link to record, update the link and show it
      // Otherwise, hide the link
      if (image.link) {
        $gallery.find('.gallery-control-link').attr('href', image.link).show();
      } else {
        $gallery.find('.gallery-control-link').hide();
      }
    },
    options: {
      images: [],
    },
  };
});
