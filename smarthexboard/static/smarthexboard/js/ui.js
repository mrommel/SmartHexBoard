/**
 * ui
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */
// import { CircularProgressBar } from "./circularProgressBar.js";

const _text_size_percentage = 0.25;
const ns = 'http://www.w3.org/2000/svg';

/**
 *
 * @param {Number} width width in px
 * @param {Number} height height in px
 * @param {String} container ID of the parent
 * @param {Object} [options] progress bar options
 * @param {Number} [options.strokeSize=1] size of the stroke
 * @param {String} [options.backgroundColor='black'] background color of the inner circle
 * @param {String} [options.strokeColor='white'] color of the stroke
 * @param {String} [options.centerIcon] icon displayed at the center of the inner circle
 * @param {Boolean} [options.showProgressNumber=false] icon displayed at the center of the inner circle
 * @param {EventListener} [options.oncomplete] callback function invoked when progress reaches 100%
 */
function CircularProgressBar(width, height, container, options) {

    const strokeSize = options.strokeSize || 1;
    const _outer_r_size = width/2 - strokeSize;
    const _inner_r_size = _outer_r_size-(strokeSize/2);
    const _stroke_percentage = strokeSize/width;
    const _inner_r_percentage = _inner_r_size/width;
    const _outer_r_percentage = _outer_r_size/width;

    this._width = width;
    this._container = document.getElementById(container);
    this._container.style.width = width + 'px';
    this._container.style.height = height + 'px';

    // create outer circle
    let outerSvg = document.createElementNS(ns,'svg');
    outerSvg.setAttribute('class','progress-ring back-ring');
    this._outerCircle = document.createElementNS(ns,'circle');
    this._outerCircle.setAttribute('class','progress-ring__circle');
    this._outerCircle.setAttribute('fill','transparent');
    this._outerCircle.setAttribute('stroke',options.strokeColor || '#fff');
    this._outerCircle.setAttribute('cx','50%');
    this._outerCircle.setAttribute('cy','50%');

    // set dynamic dim
    let strokeW = width*_stroke_percentage;
    this._outerCircle.setAttribute('stroke-width', strokeW);
    let outerRadius = width*_outer_r_percentage;
    this._outerCircle.setAttribute('r', outerRadius);
    outerSvg.appendChild(this._outerCircle);

    // create inner circle
    let innerSvg = document.createElementNS(ns,'svg');
    innerSvg.setAttribute('class','progress-ring front-ring');
    this._innerCircle = document.createElementNS(ns,'circle');
    this._innerCircle.setAttribute('class','progress-ring__circle');
    this._innerCircle.setAttribute('fill', options.backgroundColor || 'black');
    this._innerCircle.setAttribute('cx','50%');
    this._innerCircle.setAttribute('cy','50%');

    // set dynamic dim
    let innerRadius = width*_inner_r_percentage;
    this._innerCircle.setAttribute('r', innerRadius);
    innerSvg.appendChild(this._innerCircle);

    // append to _container
    this._container.appendChild(outerSvg);
    this._container.appendChild(innerSvg);

    if(options.centerIcon) this.setCenterIcon(options.centerIcon)
    if(options.showProgressNumber) this.showProgressNumber(true)
    this._oncomplete = options.oncomplete

    // save dim
    this._radius = this._outerCircle.r.baseVal.value;
    this._circumference = this._radius * 2 * Math.PI;
    this._outerCircle.style.strokeDasharray = `${this._circumference} ${this._circumference}`;

    this.setProgress(0);
}

/**
 * set color of the inner circle
 * @param {String} color a valid CSS color
 */
CircularProgressBar.prototype.setBackgroundColor = function(color) {
    this._innerCircle.setAttribute('fill', color);
}

/**
 * set color of the stroke
 * @param {String} color a valid CSS color
 */
CircularProgressBar.prototype.setStrokeColor = function(color) {
    this._outerCircle.setAttribute('stroke', color);
}

/**
 * @param {Boolean} enabled boolean to show/hide progress number
 */
CircularProgressBar.prototype.showProgressNumber = function(enabled) {
    if (enabled) {
        this._progressText = document.createElement('p');
        this._progressText.setAttribute('class','progress-text');
        this._progressText.style.fontSize = (_text_size_percentage *this._width)+'px';
        this._progressText.innerHTML = "" + this.getProgress();
        this._container.appendChild(this._progressText);
    } else {
        if (this._progressText) this._progressText.style.display = 'none';
    }
}

/**
 * set an image at the center of the progressbar
 * @param {String} src image src
 */
CircularProgressBar.prototype.setCenterIcon = function(src) {
    if (!this._icon) {
        this._icon = document.createElement('img');
        this._icon.setAttribute('class','progress-icon');
        this._icon.setAttribute('src',src);
        this._container.appendChild(this._icon);
    } else {
        this._icon.setAttribute('src',src);
    }
}

/**
 * Set progress of the progressbar (with animation);
 * @param {Number} percent progress percentage
 */
CircularProgressBar.prototype.setProgress = function(percent) {
    if(percent > 100) return
    this._progress = percent;
    this._outerCircle.style.strokeDashoffset = this._circumference - percent / 100 * this._circumference;

    if(this._progressText)
        this._progressText.innerHTML = this._progress;

    if(this._oncomplete)
        this._oncomplete();
}

/**
 * Get current progress
 * @returns {Number}
 */
CircularProgressBar.prototype.getProgress = function() {
    return this._progress || 0;
}


function UIBuilder() {

    // createMessageBox
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

    // createUnitPanel
    const $unitPanelIcon = $('#unit_panel_icon');

    const unitHealth = addTag('unit_panel_icon', 'div');
    unitHealth.id = 'unitHealth';

    this.progress = new CircularProgressBar(88, 88, 'unitHealth', {strokeSize: 6});
    this.progress.setBackgroundColor('darkcyan');
    this.progress.setStrokeColor('cyan');
    this.progress.showProgressNumber(false);
    $unitPanelIcon.append(this.progress);

    const $img = $("<img>")
        .attr('id', 'unit_panel_icon_img')
        .addClass('unit-icon')
        .attr("alt", '')
        .attr("src", '');

    $unitPanelIcon.append($img);

    console.log('created unit panel');

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

UIBuilder.prototype.unitPanel = function(unit, actions, event, callback) {
    // console.log('unitPanel: ' +  unit + ' => ' + actions);
    // console.log('unitType: ' + unit.unitType.toString());
    // console.log('texture: ' + unit.unitType.texture);
    $('#unit_panel_title').text(unit.name);
    $('#unit_panel_icon_img').attr('src', unit.icon());
    $('#unit_panel_max_moves_text').text('? / ' + unit.unitType.max_moves);

    this.progress.setProgress(80);

    const $actionPanel = $('#unit_panel_actions');
    $actionPanel.empty();

    const actionImages = new Map([
        ['ACTION_ATTACK', '/static/smarthexboard/img/ui/commands/command_button_attack@3x.png'],
        ['ACTION_DISBAND', '/static/smarthexboard/img/ui/commands/command_button_disband@3x.png'],
        ['ACTION_FOUND_CITY', '/static/smarthexboard/img/ui/commands/command_button_found@3x.png'],
        ['ACTION_SKIP', '/static/smarthexboard/img/ui/commands/command_button_skip@3x.png'],
        ['ACTION_SLEEP', '/static/smarthexboard/img/ui/commands/command_button_sleep@3x.png']
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