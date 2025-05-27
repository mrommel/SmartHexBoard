/**
 * ui
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

import { MessageView } from "./widgets/messageView.js";
import { InputView } from "./widgets/inputView.js";
import { UnitPanel } from "./widgets/unitPanel.js";
import { CityView } from "./widgets/cityView.js";

class UIBuilder {
    constructor() {
        this._messageView = new MessageView()
        this._unitPanel = new UnitPanel();
        this._inputView = new InputView();
        this._cityView = new CityView();
    }

    // message
    message(title, message, callback) {
        this._messageView.show(title, message, callback);
    }

    hideMessage() {
        this._messageView.hide();
    }

    // input
    textInput(title, text, callback) {
        this._inputView.show(title, text, callback);
    }

    hideTextInput() {
        this._inputView.hide();
    }

    // unit panel
    unitPanel(unit, actions, callback) {
        this._unitPanel.show(unit, actions, callback);
    }

    hideUnitPanel() {
        this._unitPanel.hide();
    }

    cityPanel(city, city_info, callback) {
        this._cityView.show(city, city_info, callback);
    }

    hideCityPanel() {
        this._cityView.hide();
    }
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

export { UIBuilder, UIState };