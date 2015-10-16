// adapted from https://gist.github.com/magican/5574556

define(["require", "jquery", "base/js/namespace"], function (require, $, IPython) {
  "use strict";

  var ol_depth = function (element) {
    // get depth of nested ol
    var d = 0;
    while (element.prop("tagName").toLowerCase() == 'ol') {
      d += 1;
      element = element.parent();
    }
    return d;
  };

  var make_link = function (h) {
    var a = $("<a/>");
    a.attr("href", '#' + h.attr('id'));
    // get the text *excluding* the link text, whatever it may be
    var hclone = h.clone();
    hclone.children().remove();
    a.text(hclone.text());

    return a;
  };

  var static_table_of_contents = function (threshold) {
    if (threshold === undefined) {
      threshold = 4;
    }
    var toc = $("#static-toc");
    if (toc.length === 0) {
      // No toc found. Cancel building toc
      return;
    }
  
    var ol = $("<ol/>");
    ol.addClass("toc-item");
    toc.empty().append(ol);
    
    $("#notebook").find(":header").map(function (i, h) {
      var level = parseInt(h.tagName.slice(1), 10);
      // skip below threshold
      if (level > threshold) return;
      // skip headings with no ID to link to
      if (!h.id) return;
      
      var depth = ol_depth(ol);

      // walk down levels
      for (; depth < level; depth++) {
        var new_ol = $("<ol/>");
        new_ol.addClass("toc-item");
        ol.append(new_ol);
        ol = new_ol;
      }
      // walk up levels
      for (; depth > level; depth--) {
        ol = ol.parent();
      }
      //
      ol.append(
        $("<li/>").append(make_link($(h)))
      );
    });
  };

  var htable_table_of_contents = function (threshold) {
    if (threshold === undefined) {
      threshold = 4;
    }
    var toc = $("#htable-toc");
    if (toc.length === 0) {
      // No toc found. Cancel building toc
      return;
    }
  
    var htable = $("<table/>");
    ol.addClass("toc-item");
    toc.empty().append(ol);
    
    $("#notebook").find(":header").map(function (i, h) {
      var level = parseInt(h.tagName.slice(1), 10);
      // skip below threshold
      if (level > threshold) return;
      // skip headings with no ID to link to
      if (!h.id) return;
      
      var depth = ol_depth(ol);

      // walk down levels
      for (; depth < level; depth++) {
        var new_ol = $("<ol/>");
        new_ol.addClass("toc-item");
        ol.append(new_ol);
        ol = new_ol;
      }
      // walk up levels
      for (; depth > level; depth--) {
        ol = ol.parent();
      }
      //
      ol.append(
        $("<li/>").append(make_link($(h)))
      );
    });
  };


  var findings_table_of_contents = function (threshold) {
    if (threshold === undefined) {
      threshold = 4;
    }
    var toc = $("#findings-toc");
    if (toc.length === 0) {
      // No toc found. Cancel building toc
      return;
    }
  
    var toclist = $("<ol/>");
    toclist.addClass("findings-toc-item");
    toc.empty().append(toclist);
    
    $("#notebook").find(".vuln, .warn, .info").map(function (i, h) {
      //console.log(h.tagName);
      //console.log(jQuery.text(h));
      //console.log(h.className);
      //var level = parseInt(h.tagName.slice(1), 10);
      // skip below threshold
      //if (level > threshold) return;
      // skip headings with no ID to link to
      //if (!h.id) return;

      toclist.append(
	$("<li class='"+h.className+"'/>").append(make_link($(h)))
      );
      /*  
      var depth = ol_depth(ol);

      // walk down levels
      for (; depth < level; depth++) {
        var new_ol = $("<ol/>");
        new_ol.addClass("toc-item");
        ol.append(new_ol);
        ol = new_ol;
      }
      // walk up levels
      for (; depth > level; depth--) {
        ol = ol.parent();
      }
      //
      ol.append(
        $("<li class='"+h.className+"'/>").append(make_link($(h)))
      );
      */
    });

    $(window).resize(function(){
      $('#toc').css({maxHeight: $(window).height() - 200});
    });

    $(window).trigger('resize');
  };


  var findings_table_of_contents = function (threshold) {
    if (threshold === undefined) {
      threshold = 4;
    }
    var toc = $("#findings-toc");
    if (toc.length === 0) {
      // No toc found. Cancel building toc
      return;
    }
  
    var toclist = $("<ol/>");
    toclist.addClass("findings-toc-item");
    toc.empty().append(toclist);
    
    $("#notebook").find(".vuln, .warn, .info").map(function (i, h) {

      toclist.append(
	$("<li class='"+h.className+"'/>").append(make_link($(h)))
      );

    });

    $(window).resize(function(){
      $('#toc').css({maxHeight: $(window).height() - 200});
    });

    $(window).trigger('resize');
  };
    
  
  var load_css = function () {
    var link = document.createElement("link");
    link.type = "text/css";
    link.rel = "stylesheet";
    link.href = require.toUrl("./main.css");
    document.getElementsByTagName("head")[0].appendChild(link);
  };
  
  var load_ipython_extension = function () {
    load_css();
    // $([IPython.events]).on("notebook_loaded.Notebook", table_of_contents);
    $([IPython.events]).on("notebook_saved.Notebook", findings_table_of_contents);
    $([IPython.events]).on("notebook_saved.Notebook", static_table_of_contents);
    $([IPython.events]).on("notebook_saved.Notebook", htable_table_of_contents);
    $([IPython.events]).on("rendered.MarkdownCell", findings_table_of_contents);
    $([IPython.events]).on("rendered.MarkdownCell", static_table_of_contents);
    $([IPython.events]).on("rendered.MarkdownCell", htable_table_of_contents);
	  
  };

  return {
    load_ipython_extension : load_ipython_extension,
    findings_table_of_contents : findings_table_of_contents,
    static_table_of_contents : static_table_of_contents,
    htable_table_of_contents : htable_table_of_contents
  };
});
