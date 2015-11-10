/**
 * Created by bens3 on 04/11/15.
 */

ckan.module('gallery', function (jQuery, _) {

  var self;

  return {
    initialize: function () {
        self = this
        document.domain = "nhm.ac.uk";
        $("a", this.el).each(function(i) {
            $(this).data("index", i)
            $(this).on('click', jQuery.proxy(self._openLightbox));
        });

//        $('#download-tooltip').tooltip({
//            position: { of: '#blueimp-gallery a.gallery-control-download', my: 'left+60 center', at: 'left center' },
//            tooltipClass: "download-tooltip"
//        });

//        $('#blueimp-gallery a.gallery-control-download').on('click', jQuery.proxy(self._showDownloadTooltip));
//        // Hide the tooltip if the gallery is clicked
//        $('#blueimp-gallery').on('click', jQuery.proxy(self._hideDownloadTooltip));
    },
    _getCurrentImage: function () {
        var pos = self.gallery.getIndex();
        return self.options.images[pos]
    },
    _openLightbox: function (e) {
        var options = {
            index: $(this).data("index"),
//            onclose: function () {
//                self._hideDownloadTooltip()
//            },
            onslide: function () {
                self._updateLinks()
            }
        }
        self.gallery = blueimp.Gallery(self.options.images, options)
        e.stopPropagation();
        return false;
    },
//    _showDownloadTooltip: function(e){
//        var image = self._getCurrentImage()
//        $('#download-tooltip').data("image", image).tooltip( "option", "content", self._getTooltipText(image)).tooltip('open');
//        e.stopPropagation();
//        return false;
//    },
//    _hideDownloadTooltip: function(e){
//        $('#download-tooltip').tooltip('close');
//    },
//    _getTooltipText: function(image){
//        // Get the HTML image 0 we then know the dimensions
//        $img = $('#blueimp-gallery img[src="' + image.href + '"]')
//        return '<ul><li><a href="' + image.href + '" download>Download image (' + $img[0].naturalHeight + '&times;' + $img[0].naturalWidth + ')</a></li></ul>'
//    },
    _updateLinks: function(){
        var image = self._getCurrentImage()

        // Update download link
        $('#blueimp-gallery a.gallery-control-download').attr('href', image.href);
        $('#blueimp-gallery a.gallery-control-download').on('click', jQuery.proxy(self._downloadImage));

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
    _downloadImage: function(e){
        self.downloadFile('http://www.nhm.ac.uk/services/media-store/asset/2d63e01b999aaa0581397d9e629e4bc9f30677a7/contents/preview', function(blob) {
            saveAs(blob, "image.png");
        });
        e.stopPropagation();
        return false;
    },
    downloadFile: function(url, success){
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.responseType = "blob";
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4) {
                if (success) success(xhr.response);
            }
        };
       xhr.send(null);
    },
    options: {
        images: []
    }
  };
});