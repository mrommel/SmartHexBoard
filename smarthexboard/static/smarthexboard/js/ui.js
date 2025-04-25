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

        console.log('created unit panel');
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
    /*const $actionPanelTitle = $('#action-panel-title');
    const $actionPanelItems = $('#action-panel-items');
    const $actionPanel = $('#action-panel');

    $actionPanelTitle.text(title);
    $actionPanelItems.empty();

    actions.forEach((action, index) => {
        const actionItem = `<li class="action-panel-item">${action}</li>`;
        $actionPanelItems.append(actionItem);
    });

    $('ul li').click(function(e) {
        let action = $(this).text();
        let index = $(this).index();
        callback(action, index);
    });

    const { clientX: x, clientY: y } = event;
    $actionPanel.css({ top: y + 20, left: x });*/
    makeVisible('unit_panel');
}

UIBuilder.prototype.hideUnitPanel = function() {
    makeHidden('unit_panel');
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