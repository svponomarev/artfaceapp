/*
* === ARTFACEAPP: PEOPLE PAGE SCRIPTS===
*/

var masonry_init = false; // global variable to check if masonry was initialized

$( document ).ready(function() {
    // emphasize navbar-nav for people section
    $("#menu_people").css("color", "#000");
    $("#menu_people").css("text-decoration", "underline");
    $("#1910").click(); // activate 1910 decade radio button without triggering loading
    // process click on radio buttons
    $(".btnradio").click(function(e) {
        html = $(this).html();
        input = jQuery.parseHTML(html);
        var category = input[0].getAttribute('name');
        var decade = "1910";
        var gender = "male";
        if (category == "gender") { // set new gender, get old decade
            decade = $("input[name='decade']:checked").val();
            gender = $(this).text().toLowerCase();
        }
        else { // set new decade, get old gender
            gender = $("input[name='gender']:checked").val();
            decade = $(this).text();
        }
        e.preventDefault(); // cancel default behaviour for radio buttons
        // send ajax POST request to retrieve html content for grid items with person portraits and description
        $.ajax({
            type: "POST",
            url: "/ajax_people",
            data: JSON.stringify({ "gender": gender, "decade" : decade }),
            contentType : 'application/json',
            beforeSend: function() {
                 $(".vertical-center").fadeIn(100);
            },
            success: function(json) {
                    // animate grid emergence
                    $(".grid").fadeOut(500, function() {
                        $(".grid").html(''); // clear previous content
                        if (masonry_init) {
                            $(".grid").masonry( 'destroy');
                        }
                        $.each(json.face, function() { // for each grid item generate following HTML DOM structure:
                            /** <div class='item photo'>
                                    <div class='content'>
                                        <div class='title'>
                                            <h3></h3>
                                        </div>
                                        <a><img></a>
                                        <div class='desc'><blockquote></blockquote></div>
                                    </div>  
                                </div> **/
                            var itph= $('<div>', {class: 'grid-item item photo'});
                            var itcnt = $('<div>', {class: 'content'});
                            itph.append(itcnt);
                            var tit = $('<div>', {class: 'title'});
                            itcnt.append(tit);
                            var h3 = $('<h3>', {text: this.name});
                            tit.append(h3);
                            var ref = $('<a>', {href: this.path});
                            // process years of living: is/was + spacing
                            var years = " (" + this.birth + " - ";
                            if (this.death == 0)
                                years += " ) is ";
                            else
                                years += this.death + ") was ";                    
                            var info = "<b>" + this.name + "</b>" + years + this.descr + "<br/>" + "Learn more: <a href='" + this.wiki + "'>wikipedia</a>, <a href='" + this.info + "'>" + this.source + "</a>.";
                            var img = $('<img>', {class: 'photothumb', src: this.path, alt: info});
                            ref.append(img);
                            itcnt.append(ref);
                            var desc = $('<div>', {class: 'desc'});
                            itcnt.append(desc);
                            var quote =  $('<blockquote>', {text: this.quote});
                            desc.append(quote);
                            $(".grid").append(itph).masonry( 'appended', itph );  // append generated HTML to grid
                        });
                        $(".vertical-center").fadeOut(300, function () {
                            var $grid = $('.grid').imagesLoaded( function() {
                                // init Masonry after all images have loaded
                                $grid.masonry({
                                    itemSelector: '.grid-item',
                                    columnWidth: '.grid-item',
                                    transitionDuration: 0,
                                    gutter: 10
                                });
                            });
                            masonry_init = true;
                            $(".grid").fadeIn(1000);
                        });
                        var lightbox = $('.grid a').simpleLightbox(); // activate simplelightbox.js library for image lightbox functionality
                        
                        
                  }); 
             },
            error: function(xhr, ajaxOptions, thrownError) {
                // error handling
                $(".grid").fadeOut(500, function() {
                    $(".grid").html("An error (" + xhr.status + ", " + thrownError + ") ocurred. Try to reload this page.");
                });
                $(".grid").fadeIn(1000);
                console.log('xhr:');
                console.log(xhr);
                console.log('textStatus:');
                console.log(xhr.status);
                console.log('errorThrown:');
                console.log(thrownError);
            }
        });
    });
    // click on male gender radio button to trigger content loading
    $("#male").click();

});
