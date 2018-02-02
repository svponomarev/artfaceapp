/*
* === ARTFACEAPP: VARIOUS SCRIPTS===
*/

/**
 * addHoverEffect: function for binding changing background color on hover for specific object
 * @param {object} object JS object which will be animated.
 */
function addHoverEffect(object)
{
    $(object).css("cursor", "pointer"); // show that this object is also clickable
    $(object).mouseover(function() {
        $(object).css("background", "#c8c8c8");
    });
    $(object).mouseleave(function() {
        $(object).css("background", "#e8e8e8");
    });
}
