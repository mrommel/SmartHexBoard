class InputView {
    constructor() {
        // createTextInputBox
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

    show(title, text, callback) {
        $('#ui-input-title').text(title);
        $('#ui-input-message').text(text);

        let $okay_btn = $('#ui-input-okay-uiokbut');
        $okay_btn.text('Okay');
        $okay_btn.click(function (event) {
            event.preventDefault();

            let cityName = $('#ui-input-text').val();

            makeHidden('ui-input');
            callback(cityName);
        });

        let $cancel_btn = $('#ui-input-cancel-uiokbut');
        $cancel_btn.text('Cancel');
        $cancel_btn.click(function (event) {
            event.preventDefault();

            makeHidden('ui-input');
            // game.uiMessageClicked = true;
        });

        makeVisible('ui-input');
        makeHidden('unit_panel');
    }

    hide() {
        makeHidden('ui-input');
    }
}

export { InputView }