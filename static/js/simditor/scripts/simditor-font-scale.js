(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    // AMD. Register as an anonymous module unless amdModuleId is set
    define('simditor-font-scale', ["jquery","simditor"], function (a0,b1) {
      return (root['FontScaleButton'] = factory(a0,b1));
    });
  } else if (typeof exports === 'object') {
    // Node. Does not work with strict CommonJS, but
    // only CommonJS-like environments that support module.exports,
    // like Node.
    module.exports = factory(require("jquery"),require("Simditor"));
  } else {
    root['SimditorFontScale'] = factory(jQuery,Simditor);
  }
}(this, function ($, Simditor) {

var FontScaleButton,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

FontScaleButton = (function(_super) {
  __extends(FontScaleButton, _super);

  function FontScaleButton() {
    return FontScaleButton.__super__.constructor.apply(this, arguments);
  }

  FontScaleButton.i18n = {
    'zh-CN': {
      fontScale: '字体大小'
    },
    'en-US': {
      fontScale: 'Font Size'
    }
  };

  FontScaleButton.prototype.name = 'fontScale';

  FontScaleButton.prototype.icon = 'font';

  FontScaleButton.prototype.disableTag = 'pre';

  FontScaleButton.prototype.htmlTag = 'span';

  FontScaleButton.prototype._init = function() {
    var _base;
    this.menu = [
      {
        name: '100%',
        text: '100%',
        param: '1'
      }, '|', {
        name: '150%',
        text: '150%',
        param: '1.5'
      }, {
        name: '125%',
        text: '125%',
        param: '1.25'
      }, {
        name: '75%',
        text: '75%',
        param: '.75'
      }, {
        name: '50%',
        text: '50%',
        param: '.5'
      }
    ];
    $.merge(this.editor.formatter._allowedTags, ['span']);
    $.merge(this.editor.formatter._allowedStyles['span'], ['font-size']);
    (_base = this.editor.formatter._allowedAttributes)['span'] || (_base['span'] = []);
    $.merge(this.editor.formatter._allowedAttributes['span'], ['data-font-scale']);
    return FontScaleButton.__super__._init.call(this);
  };

  FontScaleButton.prototype.setActive = function(active, param) {
    FontScaleButton.__super__.setActive.call(this, active);
    if (active) {
      param = param * 100;
    }
    this.el.removeClass('active-150 active-125 active-75 active-50');
    if (active) {
      return this.el.addClass('active active-' + param);
    }
  };

  FontScaleButton.prototype._activeStatus = function() {
    var $scale, active, range, ratio;
    range = this.editor.selection.range();
    $scale = $(range.startContainer).parents('span[data-font-scale]');
    active = $scale.length > 0;
    ratio = 1;
    if (active) {
      ratio = parseFloat($scale[0].style.fontSize);
    }
    this.setActive(active, ratio);
    return this.active;
  };

  FontScaleButton.prototype.command = function(param) {
    var $node, $scale, accept, node, nodeList, range, treeWalker, _i, _len;
    range = this.editor.selection.range();
    if (range.collapsed) {
      return;
    }
    this.editor.selection.save();
    accept = false;
    treeWalker = document.createTreeWalker(range.commonAncestorContainer, -1, {
      acceptNode: function(node) {
        var $node;
        $node = $(node);
        if ($node.is('.simditor-caret-start')) {
          accept = true;
          return NodeFilter.FILTER_REJECT;
        } else if ($node.is('.simditor-caret-end')) {
          accept = false;
          return NodeFilter.FILTER_REJECT;
        } else if (accept && node.nodeType === 3 && /\S/.test(node.nodeValue)) {
          return NodeFilter.FILTER_ACCEPT;
        } else {
          return NodeFilter.FILTER_SKIP;
        }
      }
    }, false);
    nodeList = [];
    while (treeWalker.nextNode()) {
      nodeList.push(treeWalker.currentNode);
    }
    for (_i = 0, _len = nodeList.length; _i < _len; _i++) {
      node = nodeList[_i];
      $node = $(node);
      $scale = $node.parents('span[data-font-scale]');
      if ($scale.length > 0) {
        this.split($scale);
        $node.parents('span[data-font-scale]').replaceWith($node);
      }
      if (param * 1 !== 1) {
        $node.wrap("<span data-font-scale style='font-size:" + param + "em' />");
      }
    }
    this.editor.selection.restore();
    this.editor.trigger('valuechanged');
    return $(document).trigger('selectionchange');
  };

  FontScaleButton.prototype.split = function($node) {
    var wrapper;
    wrapper = $('<div/>').append($node.clone(false).empty()).html();
    $node.contents().each(function() {
      var $n;
      $n = $(this);
      if (this.nodeType === 3) {
        if (/\S/.test(this.nodeValue)) {
          return $n.wrap(wrapper);
        } else {
          return $n.remove();
        }
      } else if (this.nodeType === 1 && $n.find('span.simditor-caret-start, span.simditor-caret-end').length > 0) {
        return split($n);
      }
    });
    return $node.replaceWith($node.contents());
  };

  return FontScaleButton;

})(Simditor.Button);

Simditor.Toolbar.addButton(FontScaleButton);

return FontScaleButton;

}));