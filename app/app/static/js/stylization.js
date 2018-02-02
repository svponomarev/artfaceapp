/*
* === ARTFACEAPP: STYLIZATION PAGE SCRIPTS===
*/

var prev_decade; // global variable (int), that stores value of decade for which was previously generated stylized images
var show_equalized; // global variable (bool), to check if one needs to show equalized and colorized image in center frame or original

/**
 * post: function for sending requests to server via form generation
 * @param {string} path path to the server page
 * @param {string} params keys and values for the body of the request
 * @param {string} method type of the request - get or post
 * See https://stackoverflow.com/questions/133925/javascript-post-request-like-a-form-submit
 */
function post(path, params, method) {
    method = method || "post"; // Set method to post by default if not specified.
    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);
    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);
            form.appendChild(hiddenField);
        }
    }
    document.body.appendChild(form);
    form.submit();
}
/**
 * addHoverHint: function for binding showing of hints to specific image
 * @param {string} img id that corresponds to the JS object, e.g. image
 * @param {string} hint id that corresponds to the JS object, e.g. hint
 */
function addHoverHint(img, hint) {
    $(img).off(); // unbind all previous animations
    $(img).hover( function() { //onmouseover
        $(hint).show();
        },
        function() { //onmouseleave
         $(hint).hide();
        }
    );
}
/**
 * applyColorization: function that starts the stylization process chain with colorization
 * @param {bool} isReload shows if we are requesting new stylization without completely refreshing the page
 */
function applyColorization(isReload) {
    $(".cssload-loader").text("Setting colors"); // change text in main loader
    $(".step-panel").hide();
     if (isReload) { // if page was previously loaded
        $(".cssload-loader").fadeIn(0); // show main loader
        $("#art-img").parent('.image-wrapper').addClass('image-wrapper--loading'); // reset loaders on stylized images
        $("#photo-img").parent('.image-wrapper').addClass('image-wrapper--loading');
    }
    $("#pic2").css("background-image", "url('" + $('#origin').attr('src') + "')"); // set background of original image as its copy to animate transition later
    $.ajax({ // send ajax POST request to get colorized version of original image from server
        type: "POST",
        url: "/ajax_color",
        tryCount : 0,
        retryLimit : 3,
        async: true,
        data: JSON.stringify({ "path": $('#origin').attr('src'), "decade" : $('#decade').val() }),
        contentType : 'application/json',
        success: 
            function(json) {
                // set background in form of colorized image for outer div containing original image
                $("#pic1").css("background-image", "url('" + json.clr_path + "')");
                // animate transition between original image and colorized version 
                $("#pic2").fadeOut(2000, // hide div pic2 with original image as background
                function() {
                      var element = $('#origin').detach(); // detach original image from pic2 div
                      $('#pic1').append(element); // place original image inside pic1 div
                      $("#pic1").fadeIn(1000); // show pic1 with colorized image as background 
                       applyEqualization(json.clr_path); // proceed to the equalization step, sending path to the colorized image
                    });       
            },
        error:
            function(xhr, ajaxOptions, thrownError) {
                    // error handling
                    if (xhr.status == 500 || xhr.status == 502) {
                        this.tryCount++;
                        if (this.tryCount <= this.retryLimit) {
                            //try again
                            $(".cssload-loader").show();
                            $.ajax(this);
                            return;
                        }
                    }
                    $(".step-panel").fadeOut(500, function() {
                        $(".step-panel").html("An error (" + xhr.status + ", " + thrownError + ") ocurred. Try to reload this page.");
                        $(".cssload-loader").hide();
                    });
                    $(".step-panel").fadeIn(500); 
                    console.log('xhr:');
                    console.log(xhr);
                    console.log('textStatus:');
                    console.log(xhr.status);
                    console.log('errorThrown:');
                    console.log(thrownError);
        }
    });
}
/**
 * applyEqualization: function that continues the stylization process with image equalization
 * @param {string} clr_path path to the colorized image
 */
function applyEqualization(clr_path) {
    $(".cssload-loader").text("Equalization"); // change text in main loader
    $.ajax({ // send ajax POST request to get equalized version of colorized image from server
        type: "POST",
        url: "/ajax_equal",
        tryCount : 0,
        retryLimit : 3,
        async: true,
        data: JSON.stringify({ "path": clr_path}),
        contentType : 'application/json',
        success: 
            function(json) {
                var old_path = $('#origin').attr('src'); //remember old path for original image
                // animate transition between colorized and equalized images
                $("#pic2").css("background-image", "url('" + json.eql_path + "')"); // set background for div pic2 in form of equalized image
                var element = $('#origin').detach(); // detach original image from pic1 div 
                $('#pic2').append(element); // place original image inside pic1 div
                addHoverHint("#origin", "#hint-img"); // add hint showing that user can switch between original image and equalized
                $("#origin").click( function() { // process click on original image frame
                    show_equalized = !show_equalized; // invert value of global variable
                    if (show_equalized) { // if we were showing original image
                        // extracting image from pic1 and adding it to pic2
                        var element = $('#origin').detach();
                        $("#pic2").append(element);
                        $("#pic2").fadeIn(500);
                        $("#hint-img").text("Switch to original");
                    } // if we were showing equalized image
                    else
                    {
                        // extracting image from pic2 and adding it to pic1
                        $("#pic2").fadeOut(500, function() {
                            var element = $('#origin').detach();
                            $("#pic1").append(element);
                            $("#pic1").fadeIn(500);
                        });
                        $("#hint-img").text("Switch to equalized");
                    }
                });
                prev_decade = $('#decade').val(); // store current processed decade into global variable
                $(".cssload-loader").text("Style transfer"); // change text in main loader
                $("#pic2").fadeIn(1000, function() {
                    $("#pic1").css("background-image", "url('" + old_path + "')"); // use old path to restore background in pic1 as original image
                    applyStyleTransfer(json.eql_path); // proceed to the stylization step, sending path to the equalized image
                });                 
            },
        error: function(xhr, ajaxOptions, thrownError) {
                    // error handling
                    if (xhr.status == 500 || xhr.status == 502) {
                        this.tryCount++;
                        if (this.tryCount <= this.retryLimit) {
                            //try again
                            $(".cssload-loader").show();
                            $.ajax(this);
                            return;
                        }
                    }
                    $(".step-panel").fadeOut(500, function() {
                        $(".step-panel").html("An error (" + xhr.status + ", " + thrownError + ") ocurred. Try to reload this page.");
                        $(".cssload-loader").hide();
                    });
                    $(".step-panel").fadeIn(500); 
                    console.log('xhr:');
                    console.log(xhr);
                    console.log('textStatus:');
                    console.log(xhr.status);
                    console.log('errorThrown:');
                    console.log(thrownError);
        }
    });
}
/**
 * reloadPanel: function for reloading step info panel with decade and art style selectors
 */
function reloadPanel() {
    $('#DecadeFilters a').removeClass('Active');
    $("#DecadeFilters a[data-preset='" + $('#decade').val() + "']").addClass('Active');       
    $(".step-panel").fadeOut(2000, function(){$(".step-panel").fadeIn(1000); $(".cssload-loader").hide();});
}
/**
 * adjustPhotoSizes: function for synchronizing height of content in photo frames with height of original image
 */
function adjustPhotoSizes() {
    $("#photo-img").css( "height", $('#origin')[0].getBoundingClientRect().height + "px" );
    $("#photo-img").css( "width", "auto");
}
/**
 * adjustContainers: function for synchronizing containers width
 */
function adjustContainers() {
    $(".container-title, .footer").css("width", $('.main-row')[0].getBoundingClientRect().width + "px");
}
// bind photo frame sizes adjusting on window resizing
window.addEventListener("resize", adjustPhotoSizes); 
window.addEventListener("resize", adjustContainers);
/**
 * applyStyleTransfer: function that finishes the stylization process in the first loading of the page
 * @param {string} eql_path path to the equalized image
 */
function applyStyleTransfer(eql_path) {
    var decade = $('#decade').val(); // read current decade from hidden input on page
    var style_num = Math.floor(Math.random() * 3); // for the first loading, generate random style with number from 0 to 2
    $.when( // sending 2 simultaneous ajax request 
        $.ajax({ // Photo Request
            type: "POST",
            url: "/ajax_photo_style",
            tryCount : 0,
            retryLimit : 3,
            async: true, // code continued, nothing get paused
            data: JSON.stringify({  "path": eql_path, "decade" : decade }),
            contentType : 'application/json',
            success: function(json){
                    $("#photo-rect").fadeOut(1500, function() {
                        $("#photo-img").attr("src", json.processed_path); // load photo stylized image
                        $("#photo-img").ready(function() {
                            // removing loader class from image
                            $("#photo-img").parent('.image-wrapper--loading').removeClass('image-wrapper--loading');
                            $("#photo-img").parent(".image-wrapper").hide();
                            // adjusting padding
                            var ratio = parseFloat(json.photo_ratio);
                            $("#photo-img").parent(".image-wrapper").css("padding-bottom",  String(ratio * 100) + "%");
                            adjustPhotoSizes();
                        });
                        addHoverHint("#photo-img", "#hint-photo"); // add hint showing that user can read more about photo style of this decade
                        $("#hint-photo").html("Learn about " +  decade + "'s photo");
                        // process click on photo stylized frame
                        $("#photo-img").click( function() {post('/art', {decade: decade, form: 'photo'});}); // send POST request to the /art page
                        $("#photo-img").parent(".image-wrapper").fadeIn(500, function() {
                            $("#photo-rect").fadeIn(500);
                        });
                    });
            },
            error: function(xhr, ajaxOptions, thrownError) {
                    // error handling
                    if (xhr.status == 500 || xhr.status == 502) {
                        this.tryCount++;
                        if (this.tryCount <= this.retryLimit) {
                            //try again
                            $(".cssload-loader").show();
                            $.ajax(this);
                            reloadPanel();
                            return;
                        }
                    }
                    $(".step-panel").fadeOut(500, function() {
                        $(".step-panel").html("An error (" + xhr.status + ", " + thrownError + ") ocurred. Try to reload this page.");
                        $(".cssload-loader").hide();
                    });
                    $(".step-panel").fadeIn(500); 
                    console.log('xhr:');
                    console.log(xhr);
                    console.log('textStatus:');
                    console.log(xhr.status);
                    console.log('errorThrown:');
                    console.log(thrownError);
            }
        }),         
        $.ajax({ // Art Request
            type: "POST",
            url: "/ajax_art_style",
            tryCount : 0,
            retryLimit : 3,
            async: true, // code continued, nothing get paused
            // orig_path is needed, because for 1960s art style face detection may be needed, which works better on unresized original image
            data: JSON.stringify({ "orig_path": $('#orig-img-path').val(), "eql_path": eql_path, "decade" : decade, "style_num" : style_num}),
            contentType : 'application/json',
            success: function(json){
                $("#art-rect").fadeOut(1000, function() {
                    $("#art-img").attr("src", json.processed_path); // load art stylized image
                    $("#art-img").ready(function() {
                        // adjusting padding
                        var ratio = parseFloat(json.art_ratio);
                        $("#art-img").parent(".image-wrapper").css("padding-bottom", String(ratio * 100) + "%");
                    });
                    // prepare style filters selectors (3 style for current decade)
                    $( "#StyleFilters a[data-preset='0']" ).text(json.style1);
                    $( "#StyleFilters a[data-preset='1']" ).text(json.style2);
                    $( "#StyleFilters a[data-preset='2']" ).text(json.style3);
                    $('#StyleFilters a').removeClass('Active');
                    $("#StyleFilters a:eq(" + style_num + ")").addClass('Active'); // show that current random selected style is active
                    // removing loader class from image
                    $("#art-img").parent('.image-wrapper--loading').removeClass('image-wrapper--loading');
                    addHoverHint("#art-img", "#hint-art"); // add hint showing that user can read more about art style of this decade
                    $("#hint-art").html("Learn about " +  decade + "'s art");
                    // process click on art stylized frame
                    $("#art-img").click( function() {post('/art', {decade: decade, form: 'art'});}); // send POST request to the /art page
                    $("#art-rect").fadeIn(500);
                    reloadPanel();
                });         
            },
            error: function(xhr, ajaxOptions, thrownError) {
                    // error handling
                    if (xhr.status == 500 || xhr.status == 502) {
                        this.tryCount++;
                        if (this.tryCount <= this.retryLimit) {
                            //try again
                            $.ajax(this);
                            reloadPanel();
                            return;
                        }
                    }
                    $(".step-panel").fadeOut(500, function() {
                        $(".step-panel").html("An error (" + xhr.status + ", " + thrownError + ") ocurred. Try to reload this page.");
                        $(".cssload-loader").hide();
                    });
                    $(".step-panel").fadeIn(500); 
                    console.log('xhr:');
                    console.log(xhr);
                    console.log('textStatus:');
                    console.log(xhr.status);
                    console.log('errorThrown:');
                    console.log(thrownError);
            }
        })
    ).then(function() { // after both requests is completed
    });
}
/**
 * reloadStyleTransfer: function that generates stylized images using path to the equalized image after loading the page
 * @param {string} eql_path path to the equalized image
 */
function reloadStyleTransfer(eql_path) {
    // assuming that page was previously loaded
    $(".step-panel").fadeOut(500, function(){ // fade out previously stylized images and footer info panel
        $(".cssload-loader").show(); // show main loader
        $("#art-img").parent('.image-wrapper').addClass('image-wrapper--loading'); // reset loaders on stylized images
        $("#photo-img").parent('.image-wrapper').addClass('image-wrapper--loading');
        applyStyleTransfer(eql_path); // call default function for stylization
    });
}
/**
 * applyArtTransfer: function that generates only art stylized image, when user switches art style for current decade
 * @param {string} eql_path path to the equalized image
 * @param {int} style_num specific style number (from 0 to 2)
 */
function applyArtTransfer(eql_path, style_num) {
    var decade = $('#decade').val(); // read current decade from hidden input on page
    $("#art-img").parent('.image-wrapper').addClass('image-wrapper--loading');
    $.ajax({ // send ajax POST request to get art stylized image from server
        type: "POST",
        url: "/ajax_art_style",
        tryCount : 0,
        retryLimit : 3,
        async: true,
        // orig_path is needed, because for 1960s art style face detection may be needed, which works better on unresized original image
        data: JSON.stringify({ "orig_path": $('#orig-img-path').val(), "eql_path": eql_path, "decade" : decade, "style_num" : style_num}),
        contentType : 'application/json',
        success: function(json) {
                $("#art-img").attr("src", json.processed_path); // load art stylized image
                $("#art-img").ready(function() {
                    // adjusting padding
                    var ratio = parseFloat(json.art_ratio);
                    $("#art-img").parent(".image-wrapper").css("padding-bottom", String(ratio * 100) + "%");
                });
                // removing loader class from image
                $("#art-img").parent('.image-wrapper--loading').removeClass('image-wrapper--loading');
                addHoverHint("#art-img", "#hint-art"); // reset hint showing that user can read more about art style of this decade
                $("#hint-art").html("Learn about " +  decade + "'s art");
                // rebind click processing on art stylized frame
                $("#art-img").click( function() {post('/art', {decade: decade, form: 'art'}); }); // send POST request to the /art page
            },
        error: function(xhr, ajaxOptions, thrownError) {
                // error handling
                if (xhr.status == 500 || xhr.status == 502) {
                        this.tryCount++;
                        if (this.tryCount <= this.retryLimit) {
                            //try again
                            $.ajax(this);
                            return;
                        }
                    }
                $(".step-panel").fadeOut(500, function() {
                    $(".step-panel").html("An error (" + xhr.status + ", " + thrownError + ") ocurred. Try to reload this page.");
                    $(".cssload-loader").hide();
                });
                $(".step-panel").fadeIn(500); 
                console.log('xhr:');
                console.log(xhr);
                console.log('textStatus:');
                console.log(xhr.status);
                console.log('errorThrown:');
                console.log(thrownError);
        }
    });
}
$( document ).ready(function() {
    adjustContainers();
    $("#back-button").click(function() { // bind redirection to previous page on click of the back-button
        window.history.back();
    });
    addHoverEffect("#back-button"); // show that back-button is already clickable
    $("#next-button").click(function() { // bind click on the next step button
        window.location.href='/'; // redirect to the main page
    });
    // set ratio for all images as for original image at first
    var ratio = parseFloat($("#hidden-ratio").val());
    $(".image-wrapper").css("padding-bottom", String(ratio * 100) + "%");
    addHoverEffect("#next-button"); // show that next-button is clickable too
    $(".hint-label").hide(); // hide all hint labels for images
    // set start values of global variables
    prev_decade = 0;
    show_equalized = true;
    $('#DecadeFilters').on('click', 'a', function() { // process click on selectors of decade    
        $('#DecadeFilters a').removeClass('Active'); // clear all selectors from active selection
        $(this).addClass('Active'); // make this selector active
        var decade = parseInt($(this).data('preset')); // get decade value from selector
        $('#decade').val(decade); // store it in hidden input on page
        var same_color = (prev_decade < 1950 && decade < 1950) || (prev_decade >= 1950 && decade >= 1950) // check if we need to recolor the image or not
        // if the page was previously loaded and current decade also does not need color (1910-1940) or also uses color (1950-2000) 
        if (prev_decade != 0 && same_color) 
        {       
            var eql_path = $('#pic2').css('background-image').split('/'); // get path of the equalized image from background-image property
            if (eql_path.length != 0) { // if background_image is still stored in browser
                var parsed = eql_path[eql_path.length-1].split("\"")[0];
                /* Edge & Safari special check */
                if (parsed[parsed.length-1] == ")")
                    parsed = parsed.substring(0, parsed.length-1);
                /* Edge & Safari special check */
                eql_path = "app/static/uploads/" + parsed; 
                reloadStyleTransfer(eql_path); // start stylization from equalized image
            }
            else
            {
                applyColorization(true); // start stylization from the beginning
            }
        }
        else
            applyColorization(true); // start stylization from the beginning
    });
    $('#StyleFilters').on('click', 'a', function() { // process click on selectors of style
        $('#StyleFilters a').removeClass('Active'); // clear all selectors from active selection
        $(this).addClass('Active'); // make this selector active
        var style_num = parseInt($(this).data('preset')); // get style number from selector
        var eql_path = $('#pic2').css('background-image').split('/'); // get path of the equalized image from background-image property
        var parsed = eql_path[eql_path.length-1].split("\"")[0];
        /* Edge & Safari special check */
        if (parsed[parsed.length-1] == ")")
            parsed = parsed.substring(0, parsed.length-1);
        /* Edge & Safari special check */
        if (eql_path.length != 0) { // if background_image is still stored in browser
            eql_path = "app/static/uploads/" + parsed;
            applyArtTransfer(eql_path, style_num); // make only art style transfer with selected style
        }
        else
            applyColorization(true); // start stylization from the beginning
    });
    applyColorization(false); // start process of stylization, decade and path to the original image is taken from hidden inputs
});
