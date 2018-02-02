/*
* === ARTFACEAPP: MATCHING PAGE SCRIPTS===
*/

/**
 * adjustWidth: function for synchronizing widths of content in frames with widths of frames
 */
function adjustWidth() {
    $( "#top1 .frame .item .photo, #top1 .match-title, #top1 .desc" ).css( "width", $( "#top1 .img-responsive" )[0].getBoundingClientRect().width + "px" );
    $( "#top2 .frame .item .photo, #top2 .match-title, #top2 .desc" ).css( "width", $( "#top2 .img-responsive" )[0].getBoundingClientRect().width + "px" );
    $( "#top3 .frame .item .photo, #top3 .match-title, #top3 .desc" ).css( "width", $( "#top3 .img-responsive" )[0].getBoundingClientRect().width + "px" );
}

// bind frame widths adjusting on window resizing
window.addEventListener("resize", adjustWidth); 

$( document ).ready(function() {
    $("#back-button").click(function() { // bind redirection to previous page on click of the back-button
        window.history.back();
    });
    $("#top1, #top2, #top3").css('opacity', '0'); // hide top matched faces at first
    // add padding for the loading wrapper (original image)
    var ratio = parseFloat($("#hidden-ratio").val());
    $("#origin").closest('.image-wrapper').css("padding-bottom", String(ratio * 100) + "%");
    // add paddings for the loading wrapper (top-3 matches)
    for (img_num = 1; img_num <= 3; img_num++) {
        var ratio = parseFloat($("#top" + String(img_num)).attr("ratio"));
        $("#top" + String(img_num) + " .image-wrapper").css("padding-bottom", String(ratio * 100) + "%");
        $("#top" + String(img_num) + " .img-responsive").css("height", "25vh");
        $("#top" + String(img_num) + " .img-responsive").css("width", "auto");
        $("#top" + String(img_num) + " .img-responsive").css("width", "auto");
    }

   if ($('.image').prop('complete')) {
      $('.image').parent().removeClass('image-wrapper--loading');
    } else {
      $('.image').on('load', function() {
        $('.image').parent().removeClass('image-wrapper--loading');
      });
    }


    addHoverEffect("#back-button"); // show that back-button is already clickable
    addHoverEffect("#next-button"); // show that next-button is clickable too (matching is super fast)
    $("#decade-select").val($("#hidden-decade").val()); // set founded decade that we get from hidden form in selector
    $("#next-button").click(function() { // bind click on the next step button
            $("#hidden-path").val($("#origin").attr('src')); // get path to original image from another hidden field in page
            $("#hidden-decade").val($("#decade-select option:selected").val()); // reload value of decade from selector in case user changed the decade manually
            $("#transfer-form").submit(); // submit POST request and move to the next step
    }); 

    // hack to synchronize content of frame with frame in situation when user zoom in or zoom out while holding mouse over frame
    window.mouseIsOver = false;
    $( "#top1 .match-content, #top2 .match-content, #top3 .match-content").bind('mouseover', function () {
        window.mouseIsOver = true;
    });
    $( "#top1 .match-content, #top2 .match-content, #top3 .match-content").bind('mouseleave', function () {
        window.mouseIsOver = false;
    });
    $( "*").bind('webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend',   
    function(e) {
    if (!window.mouseIsOver)
        adjustWidth();
    });

    var lightbox = $('.container a').simpleLightbox(); // activate simplelightbox.js library for image lightbox functionality
   $("#top1, #top2, #top3").fadeTo(1500, 1); // fade in top matched faces
});

