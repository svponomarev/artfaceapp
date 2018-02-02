/*
* === ARTFACEAPP: TECHNOLOGY PAGE SCRIPTS===
*/

/**
 * changeSelection: function for changing accordion tabs selection style
 */
function changeSelection() {
       $(this).toggleClass('panel-selected panel-unselected');
       $(".panel-heading").not(this).removeClass('panel-selected');
       $(".panel-heading").not(this).addClass('panel-unselected');
        
       var icon = $(this).find(".more-less");
       icon.toggleClass('glyphicon-plus glyphicon-minus');
       $(".more-less").not(icon).removeClass('glyphicon-minus');
       $(".more-less").not(icon).addClass('glyphicon-plus');
    
}

$( document ).ready(function() {
    // emphasize navbar-nav for technology section
    $("#menu_technology").css("color", "#000");
    $("#menu_technology").css("text-decoration", "underline");
    // process click on accordion tabs
    $('.panel-heading').on('click', changeSelection);
    // animate accordion emergence
    $("#accordion").hide();
    $("#accordion").fadeIn(1500);
    // collapse first section by default
    $("#headingOne a").click();
});
