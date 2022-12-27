/**
 * ui
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

function UIBuilder() {

}

UIBuilder.prototype.message = function(title, message) {
    $('#title').text(title);
    $('#message').text(message);
    makeVisible('ui-message');
    // TODO change to an event
    // game.uiMessageClicked = false;
    $('#uiokbut').onclick = function() { makeHidden('ui-message'); game.uiMessageClicked = true; }
}