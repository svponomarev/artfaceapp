/*
* === ARTFACEAPP: DETECTION PAGE SCRIPTS===
*/

/**
 * adjustPredictionSizes: function for adjusting sizes of prediction rectangles
 */
function adjustPredictionSizes()
{
    // origin-rect contains #origin - original image, which will be loaded first
    // we need to resize frames with predicted age and gender which have the same width, but half of the height
    $("#age-rect, #gender-rect").css( "width", $('#origin-rect')[0].getBoundingClientRect().width + "px" );
    $("#age-rect, #gender-rect").css( "height", ($('#origin-rect')[0].getBoundingClientRect().height/2 - 10) + "px" );
    // whole column with 2 frames with prediction also must be the same size as origin-rect to keep all columns in row equal
    $(".prediction-col").css("width", $('.origin-col')[0].getBoundingClientRect().width + "px" );
    $(".prediction-col").css("height", $('.origin-col')[0].getBoundingClientRect().height + "px" );
}

// bind frame sizes adjusting on window resizing
window.addEventListener("resize", adjustPredictionSizes);
 
var isProcessed = false; // global variable, to check if parameter predictions were done for current image, so we can move to the next step

$( document ).ready(function() {
    $("#age-rect, #gender-rect").hide();
    if ($('#origin').prop('complete')) { // adjust prediction rectangles after original image loading
        $("#age-rect, #gender-rect").fadeIn();
        adjustPredictionSizes();
    } else {
      $('#origin').on('load', function() {
        $("#age-rect, #gender-rect").fadeIn();
        adjustPredictionSizes();
      });
    }
    // add padding for the loading wrapper
    var ratio = parseFloat($("#hidden-ratio").val());
    $(".image-wrapper").css("padding-bottom", String(ratio * 100) + "%");
    // remove loaders after image loading
    if ($('.image').prop('complete')) {
      $('.image').parent().removeClass('image-wrapper--loading');
      adjustPredictionSizes();
    } else {
      $('.image').on('load', function() {
        $('.image').parent().removeClass('image-wrapper--loading');
        adjustPredictionSizes();
      });
    }
    $("#back-button").click(function() { // bind redirection to previous page on click of the back-button
        window.history.back();
    });
    $("#next-button").css('opacity', "0.5"); // show that next-button is inactive yet
    addHoverEffect("#back-button"); // show that back-button is already clickable
    $("#next-button").click(function() { // bind click on the next step button
        if (isProcessed) { // if parameters prediction (age & gender) is done
            // get parameters (gender & path to original image) from hidden form
            $("#hidden-path").val($("#origin").attr('src'));
            $("#hidden-gender").val($("#gender-select option:selected").val());
            $("#match-form").submit(); // send POST request to the server and move to step 2
        }
    }); 
    // hide panel with information before prediction is done
    $(".step-panel").hide();
    $.ajax({ // send ajax POST request to predict age and gender of person by face image
        type: "POST",
        url: "/ajax_prediction",
        async: true, // code continued, nothing get paused
        data: JSON.stringify({ "path": $('#origin').attr('src')}),
        contentType : 'application/json',
        complete: function() {
            $("#age-info").removeClass('panel-wrapper--loading'); // show age and gender prediction panesl
            $("#gender-info").removeClass('panel-wrapper--loading');
                $(".step-panel").fadeOut(300, function(){ // FINALE: show panel with results for current step, hide main loader
                    $(".step-panel").fadeIn(500);
                    $(".cssload-loader").hide();
                });
                $("#next-button").fadeTo(500, 1.0); // show that next-button is clickable now
                addHoverEffect("#next-button");
                if (!isProcessed)
                    isProcessed = true; // change global variable, so we can proceed to next step
        },
        success: function(json) {
            var label = "<h1 style='color:black'>" + json.age + "<h1/>"; // generate HTML for predicted age
            $("#age-label").append($(label)); // insert it in DOM structure for this page
            var prob = "<h1>" + json.age_prob + "%</h1>"; // also insert prediction certainty 
            $("#age-prob").append($(prob));

            var text = ""; // generate HTML for predicted gender
            if (json.gender == "Male") {
                text = "<img class='img-responsive gender-icon' src='app/static/images/icon-gender-male.png'>";
                $("#gender-select").val("male"); // set predicted gender in selector from step info panel
            }
            else {
                text = "<img class='img-responsive gender-icon' src='app/static/images/icon-gender-female.png'>";
                $("#gender-select").val("female");
            }
            $("#gender-label").append($(text)); // insert it in DOM structure for this page
            var prob = "<h1>" + json.gender_prob + "%</h1>"; // also insert prediction certainty 
            $("#gender-prob").append($(prob));

        },
        error: function(xhr, ajaxOptions, thrownError) {
            // error handling
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
    }); // end of ajax request for params prediction
});
