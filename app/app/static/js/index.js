/*
* === ARTFACEAPP: INDEX PAGE SCRIPTS===
*/

var img_chosen = false; // global variable, check if one of the preloaded images was selected

$( document ).ready(function() {
    $("#next-button").css('opacity', "0.5"); // next button is transparent until the image for uploading is selected
    $(".choice-row figure img").addClass('img-selected'); // activate box-shadow animation for images

    $(".choice-row figure img").click(function() { // process click event for preloaded images
        // reset box-shadow for other images
        $(".choice-row figure img").removeClass('img-chosen'); 
        $(".choice-row figure img").addClass('img-selected');
        // add box-shadow for clicked image
        $(this).removeClass('img-selected');
        $(this).addClass('img-chosen');

        if (!img_chosen) { // if this is the first selection of image
            // increase visibility for the next step button
            $("#next-button").fadeTo(500, 1.0);
            $("#next-button").css("cursor", "pointer");
            // bind hover animation for the next button
            $("#next-button").mouseover(function() {
                $("#next-button").css("background", "#c8c8c8");
            });
            $("#next-button").mouseleave(function() {
                $("#next-button").css("background", "#e8e8e8");
            });
            img_chosen = true;
        }
        $("#chosen-form input:hidden").val($(this).attr('src')); // remember user's choice in hidden form
    });

    $("#next-button").click(function() { // process click event for the next step button
        if (img_chosen) { // if preloaded image was selected
            $("#chosen-form").submit(); // send POST request with preloaded image path to server
        }
    });
    
    // activate 3rd party scripts for image uploading from computer or url
    var $imageupload = $('.imageupload');
    $imageupload.imageupload();
});
