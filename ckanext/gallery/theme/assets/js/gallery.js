/**
 * Created by bens3 on 04/11/15.
 */

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
        //            onclose: function () {
        //                self._hideDownloadTooltip()
        //            },
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
      $('#blueimp-gallery a.gallery-control-download').attr('href', image.href);
      //        $('#blueimp-gallery a.gallery-control-download').on('click', jQuery.proxy(self._downloadImage));

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
    //    _downloadImage: function(e){
    //        self.downloadFile('http://www.nhm.ac.uk/services/media-store/asset/2d63e01b999aaa0581397d9e629e4bc9f30677a7/contents/preview', function(blob) {
    //            saveAs(blob, "image.png");
    //        });
    //        e.stopPropagation();
    //        return false;
    //    },
    //    downloadFile: function(url, success){
    //        var xhr = new XMLHttpRequest();
    //        xhr.open('GET', url, true);
    //        xhr.responseType = "blob";
    //        xhr.onreadystatechange = function () {
    //            if (xhr.readyState == 4) {
    //                if (success) success(xhr.response);
    //            }
    //        };
    //       xhr.send(null);
    //    },
    options: {
      images: [],
    },
  };
});
