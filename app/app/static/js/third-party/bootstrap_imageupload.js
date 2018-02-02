/**
 * bootstrap-imageupload v1.1.2
 * https://github.com/egonolieux/bootstrap-imageupload
 * Copyright 2016 Egon Olieux
 * Released under the MIT license
 */

if (typeof jQuery === 'undefined') {
    throw new Error('bootstrap-imageupload\'s JavaScript requires jQuery.');
}

function submit(action, method, values) {
    var form = $('<form/>', {
        action: action,
        method: method
    });
    $.each(values, function() {
        form.append($('<input/>', {
            type: 'hidden',
            name: this.name,
            value: this.value
        }));    
    });
    form.appendTo('body').submit();
}

(function($) {
    'use strict';

    var options = {};

    var methods = {
        init: init,
        disable: disable,
        enable: enable,
        reset: reset
    };

    // -----------------------------------------------------------------------------
    // Plugin Definition
    // -----------------------------------------------------------------------------

    $.fn.imageupload = function(methodOrOptions) {
        var givenArguments = arguments;

        return this.filter('div').each(function() {
            if (methods[methodOrOptions]) {
                methods[methodOrOptions].apply($(this), Array.prototype.slice.call(givenArguments, 1));
            }
            else if (typeof methodOrOptions === 'object' || !methodOrOptions) {
                methods.init.apply($(this), givenArguments);
            }
            else {
                throw new Error('Method "' + methodOrOptions + '" is not defined for imageupload.');
            }
        });
    };

    $.fn.imageupload.defaultOptions = {
        allowedFormats: [ 'jpg', 'jpeg', 'png', 'gif' ],
        maxWidth: 250,
        maxHeight: 250,
        maxFileSizeKb: 2048
    };

    // -----------------------------------------------------------------------------
    // Public Methods
    // -----------------------------------------------------------------------------

    function init(givenOptions) {
        options = $.extend({}, $.fn.imageupload.defaultOptions, givenOptions);

        var $imageupload = this;
        var $fileTab = $imageupload.find('.file-tab');
        var $fileTabButton = $imageupload.find('.panel-heading .btn:eq(0)');
        var $browseFileButton = $fileTab.find('input[type="file"]');
        var $removeFileButton = $fileTab.find('.btn:eq(1)');
        var $submitFileButton = $fileTab.find('.btn:eq(2)');
        var $urlTab = $imageupload.find('.url-tab');
        var $urlTabButton = $imageupload.find('.panel-heading .btn:eq(1)');
        var $uploadUrlButton = $urlTab.find('.btn:eq(0)');
        var $removeUrlButton = $urlTab.find('.btn:eq(1)');
        var $submitUrlButton = $urlTab.find('.btn:eq(2)');

        // Do a complete reset.
        resetFileTab($fileTab);
        resetUrlTab($urlTab);
        showFileTab($fileTab);
        enable.call($imageupload);
        
        // Unbind all previous bound event handlers.
        $fileTabButton.off();
        $browseFileButton.off();
        $removeFileButton.off();
        $submitFileButton.off();
        $urlTabButton.off();
        $uploadUrlButton.off();
        $removeUrlButton.off();
        $submitUrlButton.off();

        $fileTabButton.on('click', function() {
            $(this).blur();
            showFileTab($fileTab);
        });

        $browseFileButton.on('change', function() {
            $(this).blur();
            previewImageFile($fileTab);
        });

        $removeFileButton.on('click', function() {
            $(this).blur();
            resetFileTab($fileTab);
        });

        $urlTabButton.on('click', function() {
            $(this).blur();
            showUrlTab($urlTab);
        });

        $uploadUrlButton.on('click', function() {
            $(this).blur();
            previewImageUrl($urlTab);
        });

        $removeUrlButton.on('click', function() {
            $(this).blur();
            resetUrlTab($urlTab);
        });

    }

    function disable() {
        var $imageupload = this;
        $imageupload.addClass('imageupload-disabled');
    }

    function enable() {
        var $imageupload = this;
        $imageupload.removeClass('imageupload-disabled');
    }

    function reset() {
        var $imageupload = this;
        init.call($imageupload, options);
    }

    // -----------------------------------------------------------------------------
    // Private Methods
    // -----------------------------------------------------------------------------

    function getAlertHtml(message) {
        var html = [];
        html.push('<div class="alert alert-danger alert-dismissible">');
        html.push('<button type="button" class="close" data-dismiss="alert">');
        html.push('<span>&times;</span>');
        html.push('</button>' + message);
        html.push('</div>');
        return html.join('');
    }

    function getImageThumbnailHtml(src) {
        return '<img src="' + src + '" alt="Image preview" class="thumbnail" style="margin: auto; margin-bottom: 10px; max-width: ' + options.maxWidth + 'px; max-height: ' + options.maxHeight + 'px">';
    }

    function getFileExtension(path) {
        return path.substr(path.lastIndexOf('.') + 1).toLowerCase();
    }

    function isValidImageFile(file, callback) {
        // Check file size.
        if (file.size / 1024 > options.maxFileSizeKb)
        {
            callback(false, 'File is too large (max ' + options.maxFileSizeKb + 'kB).');
            return;
        }

        // Check image format by file extension.
        var fileExtension = getFileExtension(file.name);
        if ($.inArray(fileExtension, options.allowedFormats) > -1) {
            callback(true, 'Image file is valid.');
        }
        else {
            callback(false, 'File type is not allowed.');
        }
    }

    function isValidImageUrl(url, callback) {
        var timer = null;
        var timeoutMs = 3000;
        var timeout = false;
        var image = new Image();

        image.onload = function() {
            if (!timeout) {
                window.clearTimeout(timer);

                // Strip querystring (and fragment) from URL.
                var tempUrl = url;
                if (tempUrl.indexOf('?') !== -1) {
                    tempUrl = tempUrl.split('?')[0].split('#')[0];
                }

                // Check image format by file extension.
                var fileExtension = getFileExtension(tempUrl);
                if ($.inArray(fileExtension, options.allowedFormats) > -1) {
                    callback(true, 'Image URL is valid.');
                }
                else {
                    callback(false, 'File type is not allowed.');
                }
            }
        };

        image.onerror = function() {
            if (!timeout) {
                window.clearTimeout(timer);
                callback(false, 'Image could not be found.');
            }
        };

        image.src = url;

        // Abort if image takes longer than 3000ms to load.
        timer = window.setTimeout(function() {
            timeout = true;
            image.src = '???'; // Trigger error to stop loading.
            callback(false, 'Loading image timed out.');
        }, timeoutMs);
    }

    function showFileTab($fileTab) {
        var $imageupload = $fileTab.closest('.imageupload');
        var $fileTabButton = $imageupload.find('.panel-heading .btn:eq(0)');

        if (!$fileTabButton.hasClass('active')) {
            var $urlTab = $imageupload.find('.url-tab');

            // Change active tab buttton.
            $imageupload.find('.panel-heading .btn:eq(1)').removeClass('active');
            $fileTabButton.addClass('active');

            // Hide URL tab and show file tab.
            $urlTab.hide();
            $fileTab.show();
            resetUrlTab($urlTab);
        }
    }

    function resetFileTab($fileTab) {
        $fileTab.find('.alert').remove();
        $fileTab.find('img').remove();
        $fileTab.find('.btn:eq(0)').css('float', 'left');
        $fileTab.find('.btn span').text('Browse...');
        $fileTab.find('.btn:eq(1)').hide();
        $fileTab.find('.btn:eq(2)').hide();
        $fileTab.find('input').val('');
    }
    

    function previewImageFile($fileTab) {
        var $browseFileButton = $fileTab.find('.btn:eq(0)');
        var $removeFileButton = $fileTab.find('.btn:eq(1)');
        var $submitFileButton = $fileTab.find('.btn:eq(2)');
        var $fileInput = $browseFileButton.find('input');
        
        $fileTab.find('.alert').remove();
        $fileTab.find('img').remove();
        $browseFileButton.find('span').text('Browse...');
        $removeFileButton.hide();

        // Check if file was uploaded.
        if (!($fileInput[0].files && $fileInput[0].files[0])) {
            return;
        }

        $browseFileButton.prop('disabled', true);
        
        var file = $fileInput[0].files[0];

        isValidImageFile(file, function(isValid, message) {
            if (isValid) {
                var fileReader = new FileReader();

                fileReader.onload = function(e) {
                    // Show thumbnail and remove button.
                    $fileTab.prepend(getImageThumbnailHtml(e.target.result));
                    $browseFileButton.find('span').text('Change');
                    $browseFileButton.css('float', 'none');
                    $removeFileButton.css('display', 'inline-block');
                    $submitFileButton.css('display', 'inline-block');

                };

                fileReader.onerror = function() {
                    $fileTab.prepend(getAlertHtml('Error loading image file.'));
                    $fileInput.val('');
                };

                fileReader.readAsDataURL(file);
            }
            else {
                $fileTab.prepend(getAlertHtml(message));
                $browseFileButton.find('span').text('Browse');
                $fileInput.val('');
            }

            $browseFileButton.prop('disabled', false);
        });
    }

    function showUrlTab($urlTab) {
        var $imageupload = $urlTab.closest('.imageupload');
        var $urlTabButton = $imageupload.find('.panel-heading .btn:eq(1)');

        if (!$urlTabButton.hasClass('active')) {
            var $fileTab = $imageupload.find('.file-tab');

            // Change active tab button.
            $imageupload.find('.panel-heading .btn:eq(0)').removeClass('active');
            $urlTabButton.addClass('active');

            // Hide file tab and show URL tab.
            $fileTab.hide();
            $urlTab.show();
            resetFileTab($fileTab);
        }
    }

    function resetUrlTab($urlTab) {
        $urlTab.find('.alert').remove();
        $urlTab.find('img').remove();
        $urlTab.find('.btn:eq(1)').hide();
        $urlTab.find('.btn:eq(2)').hide();
        $urlTab.find('input').val('');
    }

    function previewImageUrl($urlTab) {
        var $urlInput = $urlTab.find('input[type="text"]');
        var $uploadUrlButton = $urlTab.find('.btn:eq(0)');
        var $removeUrlButton = $urlTab.find('.btn:eq(1)');
        var $submitUrlButton = $urlTab.find('.btn:eq(2)');
        $urlTab.find('.alert').remove();
        $urlTab.find('img').remove();
        $removeUrlButton.hide();

        var url = $urlInput.val();
        if (!url) {
            $urlTab.prepend(getAlertHtml('Please enter an image URL.'));
            return;
        }

        $urlInput.prop('disabled', true);
        $uploadUrlButton.prop('disabled', true);
        
        isValidImageUrl(url, function(isValid, message) {
            if (isValid) {
                // Submit URL value.
                $urlTab.find('input[type="hidden"]').val(url);

                // Show thumbnail and remove button.
                $(getImageThumbnailHtml(url)).insertAfter($uploadUrlButton.closest('.input-group'));
                $removeUrlButton.css('display', 'inline-block');
                $submitUrlButton.css('display', 'inline-block');
            }
            else {
                $urlTab.prepend(getAlertHtml(message));
            }

            $urlInput.prop('disabled', false);
            $uploadUrlButton.prop('disabled', false);
        });
    }

    function submitImageUrl($urlTab) {
        var $urlInput = $urlTab.find('input[type="text"]');
        var $uploadUrlButton = $urlTab.find('.btn:eq(0)');
        var $removeUrlButton = $urlTab.find('.btn:eq(1)');
        var $submitUrlButton = $urlTab.find('.btn:eq(2)');
        $urlTab.find('.alert').remove();
        $urlTab.find('img').remove();
        $removeUrlButton.hide();

        var url = $urlInput.val();
        if (!url) {
            $urlTab.prepend(getAlertHtml('Please enter an image URL.'));
            return;
        }

        $urlInput.prop('disabled', true);
        $submitUrlButton.prop('disabled', true);
        
        isValidImageUrl(url, function(isValid, message) {
            if (isValid) {
                // Submit URL value.
                $urlTab.find('input[type="hidden"]').val(url);
                submit('/upload', 'POST', [
                    { name: 'url', value: url },
                ]);
            }
            else {
                $urlTab.prepend(getAlertHtml(message));
            }

            $urlInput.prop('disabled', false);
            $submitUrlButton.prop('disabled', false);
        });  
    }

}(jQuery));
