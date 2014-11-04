/**
 * PanZoomUiHandler
 *
 * Helper class for handling the panzoom UI elements
 */
function PanZoomUiHandler($element, callback, arguments){
  var self = this;
  self._$element = $element;
  self._callback = callback;
  self._arguments = arguments;
  self._interval = false;
  self._timeout = false;

  self._$element.addClass('modal-ui-visible');

  /**
   * Mouse down handler
   */
  self._$element.on('mousedown.pzuh', function(e){
    self._reset_timer();
    self.invoke();
    self._timeout = window.setTimeout(function(){
      self._reset_timer();
      self.invoke();
      self._interval = window.setInterval(function(){
        self.invoke();
      }, 50);
    }, 250);
  });

  /**
   * Mouse up, mouse leave handlers
   */
  self._$element.on('mouseup.pzuh', function(){self._reset_timer()});
  self._$element.on('mouseleave.pzuh', function(){self._reset_timer()});

  /**
   * Clear the handler
   */
  self.remove = function(){
    self._reset_timer();
    self._$element.removeClass('modal-ui-visible');
    self._$element.off('mousedown.pzuh');
    self._$element.off('mouseup.pzuh');
    self._$element.off('mouseleave.pzuh');
  };

  /**
   * Invoke the handler
   */
  self.invoke = function(){
    self._callback.apply(this, self._arguments);
  };

  /**
   * Reset the timeout/interval
   */
  self._reset_timer = function(){
    if (self._timeout){
      window.clearTimeout(self._timeout);
      self._timeout = false;
    }
    if (self._interval){
      window.clearInterval(self._interval);
      self._interval = false;
    }
  };
}

/**
 * ckan gallery module
 *
 * Adds functionality to the bootstrap-gallery based gallery
 */
this.ckan.module('gallery', function($, _){
  var self;
  return {
    /**
     * Initialize the gallery module
     */
    initialize: function(){
      self = this;
      self._$img = null;
      self._panzoom_handlers = [];
      self.el.on('displayed', function(){
        self._$img = self.$('div.modal-image img');
      });
      // 'displayed' only triggers on new images.
      var already_displayed = self.$('div.modal-image img').length > 0;
      if (already_displayed){
        self._$img = self.$('div.modal-image img');
      }
      if (self._browser_supports_panzoom()){
        self.el.on('displayed', self._initialize_panzoom);
        if (already_displayed){
          self._initialize_panzoom();
        }
      }
    },

    /**
     * Initialize the panzoom functionality
     */
    _initialize_panzoom: function(){
      self._panzoom_mouse_reset();
      self._panzoom_handlers_reset();
      var options = {
        minScale: 1,
        maxScale: self._$img[0].naturalWidth / self._$img[0].clientWidth,
        contain: 'invert',
        increment: 0.1
      };
      if (options.maxScale > 1) {
        self._panzoom_handlers.push(new PanZoomUiHandler(
            self.$('div.modal-ui a.modal-ui-zoomin'),
            self._zoom_image,
            [false]
        ));
        self._panzoom_handlers.push(new PanZoomUiHandler(
            self.$('div.modal-ui a.modal-ui-zoomout'),
            self._zoom_image,
            [true]
        ));
        self._panzoom_handlers.push(new PanZoomUiHandler(
            self.$('div.modal-ui a.modal-ui-panleft'),
            self._pan_image_by,
            [10, 0]
        ));
        self._panzoom_handlers.push(new PanZoomUiHandler(
            self.$('div.modal-ui a.modal-ui-panright'),
            self._pan_image_by,
            [-10, 0]
        ));
        self._panzoom_handlers.push(new PanZoomUiHandler(
            self.$('div.modal-ui a.modal-ui-panup'),
            self._pan_image_by,
            [0, 10]
        ));
        self._panzoom_handlers.push(new PanZoomUiHandler(
            self.$('div.modal-ui a.modal-ui-pandown'),
            self._pan_image_by,
            [0, -10]
        ));
        self._$img.off('mousewheel');
        self._$img.panzoom(options).on('mousewheel', self._panzoom_mouse_wheel);
      }
    },

    /**
     * Zoom the image
     */
    _zoom_image: function(zoom_out){
      self._$img.panzoom('zoom', zoom_out);
    },

    /**
     * Pan the image
     */
    _pan_image_by: function(x, y){
      self._$img.panzoom('pan', x, y, {relative: true});
    },

    /**
     * React to mouse wheel events on the image for zoom
     */
    _panzoom_mouse_wheel: function(e){
      var $img = $(this);
      e.preventDefault();
      var delta = e.delta || e.originalEvent.wheelDelta;
      var zoomOut = delta ? delta < 0 : e.originalEvent.deltaY > 0;
      $img.panzoom('zoom', zoomOut, {
        increment: 0.1,
        animate: false,
        focal: e
      });
    },

    /**
     * Ensure the bootstrap gallery mouse handling won't interfere with our
     * zoom functionality.. This is linked to the bootstrap gallery version used.
     */
    _panzoom_mouse_reset: function(){
        self.$('div.modal-image').off('click.modal-gallery');
        $(document).off('mousewheel');
    },

    /**
     * Reset the panzoom ui element handlers
     */
    _panzoom_handlers_reset: function(){
      for (var i in self._panzoom_handlers){
        self._panzoom_handlers[i].remove();
      }
      self._panzoom_handlers = [];
    },

    /**
     * Check that the browser supported the functionality we need for panzoom
     * (typically, IE9+)
     */
    _browser_supports_panzoom: function(){
      var img = new Image();
      return ('naturalWidth' in img) && ('naturalHeight' in img);
    }
  };
});