/*
* === ARTFACEAPP: ART PAGE SCRIPTS===
*/

$( document ).ready(function() {
    // emphasize navbar-nav for art section
    $("#menu_art").css("color", "#000");
    $("#menu_art").css("text-decoration", "underline");
    // get decade and art form from hidden inputs in page (loaded with POST request)
    var decade = $("#decade").val();
    var form = $("#form").val();
    $("#" + decade).click(); // activate current decade radio button without triggering loading
    // process click on radio buttons
    $(".btnradio").click(function(e) {
        html = $(this).html();
        input = jQuery.parseHTML(html);
        var category = input[0].getAttribute('name');
        if (category == "form") {   // set new form, get old decade
            decade = $("input[name='decade']:checked").val();
            form = $(this).text().toLowerCase();
        }
        else {  // set new decade, get old form
            form = $("input[name='form']:checked").val();
            decade = $(this).text();
        }
        e.preventDefault(); // cancel default behaviour for radio buttons
        // send ajax POST request to retrieve html content for article about chosen decade and art form
        $.ajax({
            type: "POST",
            url: "/ajax_art",
            data: JSON.stringify({ "form": form, "decade" : decade }),
            contentType : 'application/json',
            beforeSend: function() {
                 $(".vertical-center").fadeIn(100);
            },
            success: function(json) {
                // animate content emergence
                $(".art-info-container").fadeOut(500, function() {
                    $(".vertical-center").fadeOut(100);
                    $(".art-info-container").html(json.style_info);
                });
                $(".art-info-container").fadeIn(1000); 
            },
            error: function(xhr, ajaxOptions, thrownError) {
                // error handling
                $(".art-info-container").fadeOut(500, function() {
                    $(".art-info-container").html("An error (" + xhr.status + ", " + thrownError + ") ocurred. Try to reload this page.");
                });
                $(".art-info-container").fadeIn(1000);
                console.log('xhr:');
                console.log(xhr);
                console.log('textStatus:');
                console.log(xhr.status);
                console.log('errorThrown:');
                console.log(thrownError);
            }
        });
    });
    // click on form radio button to trigger content loading
    $("#" + form).click();
});
