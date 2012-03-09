/*
 * 
 * Textarea Maxlength Setter JQuery Plugin 
 * Version 1.0
 * 
 * Copyright (c) 2008 Viral Patel
 * website : http://viralpatel.net/blogs
 * 
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 * 
*/

jQuery.fn.maxlength = function(){
	
	$("textarea[@maxlength]").keypress(function(event){ 
		var key = event.which;
		
		//all keys including return.
		if(key >= 33 || key == 13) {
			var maxLength = $(this).attr("maxlength");
			var length = this.value.length;
			if(length >= maxLength) {
				
				event.preventDefault();
			}
		}
	});

}

// That Matt, Updated textarea maxlength with Jquery plugin
// http://that-matt.com/2010/04/updated-textarea-maxlength-with-jquery-plugin/
jQuery.fn.limitMaxlength = function (options) {

    var settings = jQuery.extend({
        attribute: "maxlength",
        onLimit: function () { },
        onEdit: function () { }
    }, options);

    // Event handler to limit the textarea
    var onEdit = function () {
        var textarea = jQuery(this);
        var maxlength = parseInt(textarea.attr(settings.attribute));

        if (textarea.val().length > maxlength) {
            textarea.val(textarea.val().substr(0, maxlength));

            // Call the onlimit handler within the scope of the textarea
            jQuery.proxy(settings.onLimit, this)();
        }

        // Call the onEdit handler within the scope of the textarea
        jQuery.proxy(settings.onEdit, this)(maxlength - textarea.val().length);
    }

    this.each(onEdit);

    return this.keyup(onEdit)
				.keydown(onEdit)
				.focus(onEdit)
				.live('input paste', onEdit);
};
