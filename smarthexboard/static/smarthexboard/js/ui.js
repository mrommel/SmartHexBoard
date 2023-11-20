/**
 * ui
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

function UIBuilder() {

    createMessageBox();

    function createMessageBox() {
        var ui_message = addTag('ui', 'div');
        ui_message.id = 'ui-message';

        var ui_message_header = addTag(ui_message, 'div');
        ui_message_header.id = 'header';

        var ui_message_title = addTag(ui_message_header, 'div');
        ui_message_title.id = 'title';

        var ui_message_message = addTag(ui_message, 'div');
        ui_message_message.id = 'message';

        var ui_message_footer = addTag(ui_message, 'div');
        ui_message_footer.id = 'footer';

        var ui_message_button = addTag(ui_message_footer, 'div');
        ui_message_button.id = 'uiokbut';
    }
}

UIBuilder.prototype.message = function(title, message) {
    $('#title').text(title);
    $('#message').text(message);
    makeVisible('ui-message');
    // TODO change to an event
    // game.uiMessageClicked = false;
    $('#uiokbut').click(function (event) {
        event.preventDefault();

        makeHidden('ui-message');
        // game.uiMessageClicked = true;
    });
}

// https://masteringjs.io/tutorials/fundamentals/enum
class UIState {
    static splash = new UIState('Splash');
    static menu = new UIState('Menu');
    static createGame = new UIState('CreateGame')
    static generate = new UIState('Generate');
    static game = new UIState('Game');
    static gameMenu = new UIState('GameMenu');

    static options = new UIState('Options');
    static tutorials = new UIState('Tutorials');

    constructor(name) {
        this.name = name;
    }

    toString() {
        return `UIState.${this.name}`;
    }
}