/**
 * Created by bens3 on 04/11/15.
 */

ckan.module('gallery', function (jQuery, _) {

  var self;

  return {
    initialize: function () {
        self = this
        $("a", this.el).each(function(i) {
            $(this).data("index", i)
            $(this).on('click', jQuery.proxy(self._openLightbox));
        });

        $('#download-tooltip').tooltip({
            position: { of: '#blueimp-gallery a.gallery-control-download', my: 'left+60 center', at: 'left center' },
            tooltipClass: "download-tooltip"
        });

        $('#blueimp-gallery a.gallery-control-download').on('click', jQuery.proxy(self._showDownloadTooltip));
        // Hide the tooltip if the gallery is clicked
        $('#blueimp-gallery').on('click', jQuery.proxy(self._hideDownloadTooltip));
    },
    _getCurrentImage: function () {
        var pos = self.gallery.getIndex();
        return self.options.images[pos]
    },
    _openLightbox: function (e) {
        var options = {
            index: $(this).data("index"),
            onclose: function () {
                self._hideDownloadTooltip()
            },
            onslide: function () {
                self._updateViewLink()
            }
        }
        self.gallery = blueimp.Gallery(self.options.images, options)
        e.stopPropagation();
        return false;
    },
    _showDownloadTooltip: function(e){
        var image = self._getCurrentImage()
        $('#download-tooltip').data("image", image).tooltip( "option", "content", self._getTooltipText(image)).tooltip('open');
        e.stopPropagation();
        return false;
    },
    _hideDownloadTooltip: function(e){
        $('#download-tooltip').tooltip('close');
    },
    _getTooltipText: function(image){
        // Get the HTML image 0 we then know the dimensions
        $img = $('#blueimp-gallery img[src="' + image.href + '"]')
        return '<ul><li><a href="' + image.href + '" download>Download image (' + $img[0].naturalHeight + '&times;' + $img[0].naturalWidth + ')</a></li></ul>'
    },
    _updateViewLink: function(){
        var image = self._getCurrentImage()

        if(image.copyright){
            $('#blueimp-gallery .copyright').html(image.copyright)
        }
        // If we have a link to record, update the link and show it
        // Otherwise, hide the link
        if(image.link){
            $('#blueimp-gallery .gallery-control-link').attr('href', image.link).show()
        }else{
            $('#blueimp-gallery .gallery-control-link').hide()
        }
    },
    options: {
        images: []
    }
  };
});