/*
* === ARTFACEAPP: ABOUT PAGE SCRIPTS===
*/

$( document ).ready(function() {
    // emphasize navbar-nav for about section
    $("#menu_about").css("color", "#000");
    $("#menu_about").css("text-decoration", "underline");
    // animate content emergence
    $("#about_content").hide();
    $("#about_content").fadeIn(1500);
}); 
