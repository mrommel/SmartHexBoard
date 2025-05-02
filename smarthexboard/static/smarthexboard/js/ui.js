/**
 * ui
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

function UIBuilder() {

    createMessageBox();
    createUnitPanel();
    createTextInputBox();

    function createMessageBox() {
        const ui_message = addTag('ui', 'div');
        ui_message.id = 'ui-message';

        const ui_message_header = addTag(ui_message, 'div');
        ui_message_header.id = 'ui-message-header';

        const ui_message_title = addTag(ui_message_header, 'div');
        ui_message_title.id = 'ui-message-title';

        const ui_message_message = addTag(ui_message, 'div');
        ui_message_message.id = 'ui-message-message';

        const ui_message_footer = addTag(ui_message, 'div');
        ui_message_footer.id = 'ui-message-footer';

        const ui_message_button = addTag(ui_message_footer, 'div');
        ui_message_button.id = 'ui-message-uiokbut';

        console.log('created ui message box');
    }

    function createUnitPanel() {
        // const unit_icon = addTag('unit_panel', 'div');
        // unit_icon.id = 'action-panel';
        $(".unit-command").each(function () {
            this.addEventListener("click", function() {
                console.log('clicked drag');
            });
            console.log('added clicked');
        });

        console.log('created unit panel');
    }

    function createTextInputBox() {
        const ui_input = addTag('ui', 'div');
        ui_input.id = 'ui-input';

        const ui_input_header = addTag(ui_input, 'div');
        ui_input_header.id = 'ui-input-header';

        const ui_input_title = addTag(ui_input_header, 'div');
        ui_input_title.id = 'ui-input-title';

        const ui_input_body = addTag(ui_input, 'div');
        ui_input_body.id = 'ui-input-body';

        const ui_input_message = addTag(ui_input_body, 'div');
        ui_input_message.id = 'ui-input-message';

        const ui_input_text = addTag(ui_input_body, 'input');
        ui_input_text.id = 'ui-input-text';
        ui_input_text.type = 'text';

        const ui_input_footer = addTag(ui_input, 'div');
        ui_input_footer.id = 'ui-input-footer';

        const ui_input_okay_button = addTag(ui_input_footer, 'div');
        ui_input_okay_button.id = 'ui-input-okay-uiokbut';

        const ui_input_cancel_button = addTag(ui_input_footer, 'div');
        ui_input_cancel_button.id = 'ui-input-cancel-uiokbut';

        console.log('created ui input box');
    }
}

UIBuilder.prototype.message = function(title, message) {
    $('#ui-message-title').text(title);
    $('#ui-message-message').text(message);
    makeVisible('ui-message');
    // TODO change to an event
    // game.uiMessageClicked = false;
    $('#ui-message-uiokbut').click(function (event) {
        event.preventDefault();

        makeHidden('ui-message');
        // game.uiMessageClicked = true;
    });
}

UIBuilder.prototype.unitPanel = function(title, actions, event, callback) {
    console.log('unitPanel', title, actions/*, event, callback*/);
    $('#unit_panel_title').text(title);

    const $actionPanel = $('#unit_panel_actions');
    $actionPanel.empty();

    const actionImages = new Map([
        ['ACTION_ATTACK', '/static/smarthexboard/img/ui/commands/command_button_attack@3x.png'],
        ['ACTION_DISBAND', '/static/smarthexboard/img/ui/commands/command_button_disband@3x.png'],
        ['ACTION_FOUND_CITY', '/static/smarthexboard/img/ui/commands/command_button_found@3x.png']
    ]);

    actions.forEach((action, index) => {
        const actionImage = actionImages.get(action) || '/static/smarthexboard/img/ui/commands/command_button_default@3x.png';

        const $img = $("<img>")
            .addClass('unit-command')
            .attr("alt", action)
            .attr("src", actionImage)
            .attr("href", '#')
            .click(() => {
                console.log('Clicked ' + action);
                callback(action, index);
            });

        $actionPanel.append($img);
    });

    makeVisible('unit_panel');
}

UIBuilder.prototype.hideUnitPanel = function() {
    makeHidden('unit_panel');
}

UIBuilder.prototype.textInput = function(title, text, callback) {
    $('#ui-input-title').text(title);
    $('#ui-input-message').text(text);

    $('#ui-input-okay-uiokbut').text('Okay');
    $('#ui-input-okay-uiokbut').click(function (event) {
        event.preventDefault();

        let cityName = $('#ui-input-text').val();

        makeHidden('ui-input');
        callback(cityName);
    });

    $('#ui-input-cancel-uiokbut').text('Cancel');
    $('#ui-input-cancel-uiokbut').click(function (event) {
        event.preventDefault();

        makeHidden('ui-input');
        // game.uiMessageClicked = true;
    });

    makeVisible('ui-input');
    makeHidden('unit_panel');
}

UIBuilder.prototype.hideTextInput = function() {
    makeHidden('ui-input');
}

// https://masteringjs.io/tutorials/fundamentals/enum
class UIState {
    static splash = new UIState('Splash');
    static menu = new UIState('Menu');
    static playGame = new UIState('PlayGame');
    static createGame = new UIState('CreateGame');
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