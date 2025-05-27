class MessageView {
    constructor() {
        // createMessageBox
        const ui_message = addTag('ui', 'div');
        ui_message.id = 'ui-message';

        const ui_message_header = addTag(ui_message, 'div');
        ui_message_header.id = 'ui-message-header';

        const ui_message_title = addTag(ui_message_header, 'div');
        ui_message_title.id = 'ui-message-title';

        const ui_message_body = addTag(ui_message, 'div');
        ui_message_body.id = 'ui-message-body';

        const ui_message_message = addTag(ui_message_body, 'div');
        ui_message_message.id = 'ui-message-message';

        const ui_message_footer = addTag(ui_message, 'div');
        ui_message_footer.id = 'ui-message-footer';

        const ui_message_okay_button = addTag(ui_message_footer, 'div');
        ui_message_okay_button.id = 'ui-message-okay-uiokbut';

        const ui_message_cancel_button = addTag(ui_message_footer, 'div');
        ui_message_cancel_button.id = 'ui-message-cancel-uiokbut';

        console.log('created ui message box');
    }

    show(title, message, callback) {
        $('#ui-message-title').text(title);
        $('#ui-message-message').text(message);

        let $okay_btn = $('#ui-message-okay-uiokbut');
        $okay_btn.text('Okay');
        $okay_btn.click(function (event) {
            event.preventDefault();
            makeHidden('ui-message');
            callback();
        });

        let $cancel_btn = $('#ui-message-cancel-uiokbut');
        $cancel_btn.text('Cancel');
        $cancel_btn.click(function (event) {
            event.preventDefault();

            makeHidden('ui-message');
            // game.uiMessageClicked = true;
        });

        makeVisible('ui-message');
        makeHidden('ui-input');
        makeHidden('unit_panel');
    }
}

export { MessageView }