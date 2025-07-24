/*================
 Template Name: Datrics Data Science & Analytics HTML Template
 Description: All type of data science, artificial intelligence & machine learning template.
 Version: 1.0
 Author: MiRo
=======================*/

import { MouseInfo, CGPoint } from './base/prototypes.js';
import { HexPoint } from './base/point.js';
// import { TerrainTypes, FeatureTypes, ResourceTypes } from './map/types.js';
import { Map } from './map/map.js';
// import { MapOptions, MapGenerator } from './map/generator.js';
import { Renderer } from './renderer.js';
import { unitActions } from "./actions/unit.js";
import { cityInfoAt } from "./actions/city.js"
import { ActionState } from "./actions/actions.js";
import { handleError } from "./errorHandling.js";
import "./widgets/widgets.js";
import { UIState, UIBuilder } from "./ui.js";

// TABLE OF CONTENTS
// 1. preloader
// 2. canvas full screen

jQuery(function ($) {

    'use strict';

    $(document).ready(function () {
        initUI();
    });
}); // JQuery end

const mouse = {x: 0, y: 0};
let mouseLeftIsDown = false;
let mouseRightIsDown = false;
const offset = {x: 0, y: 0};
let cursor = new HexPoint(0, 0);

const renderer = new Renderer(null);
const uiRenderer = new UIBuilder();
let uiState = UIState.splash;
let actionState = ActionState.none;

function preventExitOnReload(event) {
    // Cancel the event as stated by the standard.
    event.preventDefault();
    // Chrome requires returnValue to be set.
    event.returnValue = '';
}

window.resizeCanvas = function resizeCanvas() {
    if (uiState === UIState.game) {
        drawMap();
    }
}

function drawMap() {
    if (renderer.texturesLoaded()) {
        setupCanvas();

        // Full page rendering
        renderer.render();
    } else {
        console.log('textures not initialized yet');
    }
}

function setupCanvas(canvasSize) {
    if (!renderer.texturesLoaded()) {
        return;
    }

    if (typeof (canvasSize) == 'undefined') {
        canvasSize = renderer.map.canvasSize();
    }

    // get the canvas
    const terrainsCanvas = document.getElementById('terrains');
    terrainsCanvas.width = canvasSize.width;
    terrainsCanvas.height = canvasSize.height;

    const resourcesCanvas = document.getElementById('resources');
    resourcesCanvas.width = canvasSize.width;
    resourcesCanvas.height = canvasSize.height;

    const featuresCanvas = document.getElementById('features');
    featuresCanvas.width = canvasSize.width;
    featuresCanvas.height = canvasSize.height;

    const citiesCanvas = document.getElementById('cities');
    citiesCanvas.width = canvasSize.width;
    citiesCanvas.height = canvasSize.height;

    const citiesBannerCanvas = document.getElementById('citiesBanner');
    citiesBannerCanvas.width = canvasSize.width;
    citiesBannerCanvas.height = canvasSize.height;

    const unitsCanvas = document.getElementById('units');
    unitsCanvas.width = canvasSize.width;
    unitsCanvas.height = canvasSize.height;

    const cursorCanvas = document.getElementById('cursor');
    cursorCanvas.width = canvasSize.width;
    cursorCanvas.height = canvasSize.height;

    document.getElementById('game').style.width = window.innerWidth + "px";
    document.getElementById('game').style.height = window.innerHeight + "px";

    // attach mouse events
    const vp = document.getElementById('game');

    vp.addEventListener("mousedown", handleMouseDown, true);
    vp.addEventListener("mousemove", handleMouseMove, true);
    vp.addEventListener("mouseup", handleMouseUp, true);
    vp.addEventListener("mouseleave", handleMouseLeave, true);
    vp.addEventListener('contextmenu', handleContextMenu, true);  // needed for the right click capturing
}

/*function getMouseInfo(canvas, e) {
	var mx, my, right_click;
	var viewport = document.getElementById("terrains");
	if (e.which) right_click = (e.which == 3);
	else if (e.button) right_click = (e.button == 2);

	mx = e.pageX - canvas.offsetLeft - viewport.clientLeft - viewport.offsetLeft + viewport.scrollLeft;
	my = e.pageY - canvas.offsetTop - viewport.clientTop - viewport.offsetTop + viewport.scrollTop;

	return new MouseInfo(mx, my, right_click);
}*/

function handleContextMenu(event) {
    // console.log('handleContextMenu which=' + event.which + ', button=' + event.button);
    event.preventDefault();
}

function handleMouseDown(event) {
    // console.log('handleMouseDown which=' + event.which + ', button=' + event.button + ', ctrlKey=' + event.ctrlKey);
    const leftButtonDown = (event.which === 1 && !event.ctrlKey);
    const rightButtonDown = (event.which === 1 && event.ctrlKey);

    const new_cursor = locationFromEvent(event);

    if (leftButtonDown) {
        mouseLeftIsDown = true;
    } else if (rightButtonDown) {
        mouseRightIsDown = true;

        // set cursor to new position
        renderer.renderCursor(new_cursor);
        cursor = new_cursor;
    }

    return false;
}

function handleMouseMove(event) {
    // console.log('mouse move: ' + mouse.x + ', ' + mouse.y + ' mouseLeftIsDown=' + mouseLeftIsDown);
    event.preventDefault();
	mouse.x = event.pageX;
    mouse.Y = event.pageY;

    /*const viewport = document.getElementById('game');
    const canvas = document.getElementById('terrains');

    let mx = event.pageX - canvas.offsetLeft - viewport.clientLeft - viewport.offsetLeft + viewport.scrollLeft;
    let my = event.pageY - canvas.offsetTop - viewport.clientTop - viewport.offsetTop + viewport.scrollTop;

    const canvasSize = renderer.map.canvasSize();
    const canvasOffset = renderer.map.canvasOffset();

    mx = mx - canvasOffset.x;
    my = my - canvasOffset.y;
    my = canvasSize.height - (my + canvasOffset.y) - canvasOffset.y + 30;

    const screen_position = new CGPoint(mx, my);
    const map_position = new HexPoint(screen_position);

    let terrainText = '<invalid>';
    let hillsText = ' (no hills)';
    let climateZoneText = '<invalid>';
    let resourceText = '<invalid>';
    let unitsText = '[]';

    if (renderer.map.valid(map_position)) {
        terrainText = renderer.map.terrainAt(map_position);
        if (renderer.map.isHillsAt(map_position)) {
            hillsText = ' (has hills)';
        } else {
            hillsText = '';
        }
        climateZoneText = renderer.map.climateZoneAt(map_position);
        resourceText = renderer.map.resourceAt(map_position);
        unitsText = 'Units: ' + renderer.map.unitsAt(map_position);
    } else {
        terrainText = '';
        hillsText = '';
        climateZoneText = '';
        resourceText = '';
        unitsText = 'Units: []';
    }

    const tooltipSpan = document.getElementById('tooltip');
    const x = event.clientX, y = event.clientY;
    tooltipSpan.style.top = (y + 20) + 'px';
    tooltipSpan.style.left = (x + 0) + 'px';
    tooltipSpan.style.display = 'block';
    tooltipSpan.innerHTML = 'point: ' + map_position + '<br />' + terrainText + hillsText + '<br />' + resourceText + '<br />' + climateZoneText + '<br />' + unitsText;*/

    if (mouseLeftIsDown) {
        const terrainsCanvas = document.getElementById('terrains');
        terrainsCanvas.style.left = (event.clientX + offset.x) + 'px';
        terrainsCanvas.style.top  = (event.clientY + offset.y) + 'px';

        const featuresCanvas = document.getElementById('features');
        featuresCanvas.style.left = (event.clientX + offset.x) + 'px';
        featuresCanvas.style.top  = (event.clientY + offset.y) + 'px';

        const resourcesCanvas = document.getElementById('resources');
        resourcesCanvas.style.left = (event.clientX + offset.x) + 'px';
        resourcesCanvas.style.top  = (event.clientY + offset.y) + 'px';

        const citiesCanvas = document.getElementById('cities');
        citiesCanvas.style.left = (event.clientX + offset.x) + 'px';
        citiesCanvas.style.top  = (event.clientY + offset.y) + 'px';

        const citiesBannerCanvas = document.getElementById('citiesBanner');
        citiesBannerCanvas.style.left = (event.clientX + offset.x) + 'px';
        citiesBannerCanvas.style.top  = (event.clientY + offset.y) + 'px';

        const unitsCanvas = document.getElementById('units');
        unitsCanvas.style.left = (event.clientX + offset.x) + 'px';
        unitsCanvas.style.top  = (event.clientY + offset.y) + 'px';

        const cursorCanvas = document.getElementById('cursor');
        cursorCanvas.style.left = (event.clientX + offset.x) + 'px';
        cursorCanvas.style.top  = (event.clientY + offset.y) + 'px';
        // console.log('move: x=' + vp.style.left + ' y=' + vp.style.top);

        uiRenderer.hideUnitPanel();
    }
}

function locationFromEvent(event) {
    const viewport = document.getElementById('game');
    const canvas = document.getElementById('terrains');
    offset.x = canvas.offsetLeft - event.clientX;
    offset.y = canvas.offsetTop - event.clientY;

    let mx = event.pageX - canvas.offsetLeft - viewport.clientLeft - viewport.offsetLeft + viewport.scrollLeft;
    let my = event.pageY - canvas.offsetTop - viewport.clientTop - viewport.offsetTop + viewport.scrollTop;

    const canvasSize = renderer.map.canvasSize();
    const canvasOffset = renderer.map.canvasOffset();

    mx = mx - canvasOffset.x;
    my = my - canvasOffset.y;
    my = canvasSize.height - (my + canvasOffset.y) - canvasOffset.y + 30;

    const screen_position = new CGPoint(mx, my);
    return new HexPoint(screen_position);
}

let game_id;

function handleMouseUp(event) {
    if (mouseRightIsDown) {
        const new_cursor = locationFromEvent(event);
        let units = renderer.map.unitsAt(cursor);
        let city = renderer.map.cityAt(cursor);

        console.log('handleMouseUp: ' + cursor + ' to ' + new_cursor + ' units: ' + units.length + ' city: ' + city);

        if (new_cursor.x === cursor.x && new_cursor.y === cursor.y) {
            // double click detected
            if (city != null) {
                console.log('city action at ' + new_cursor + ' for ' + city);
                cityInfoAt(city.location, game_id, function(city_info) {
                    uiRenderer.cityPanel(city, city_info, function(action, action_index) {
                        console.log('city action clicked: ' + action + ' index: ' + action_index);
                        // switch (action) {
                        //     case 'ACTION_DISBAND':
                        //         changeActionState(ActionState.disbandUnit);
                        //         break;
                        //     default:
                        //         console.log('action ' + action + ' not handled');
                        // }
                    });
                });
            } else if (units.length > 0) {
                let firstUnit = units[0];
                console.log('unit action at ' + new_cursor + ' for ' + firstUnit);
                unitActions(firstUnit, game_id, function(unit, actions) {
                    showUnitPanel(unit, event, actions);
                });
            } else {
                // console.log('no unit at ' + new_cursor);
                uiRenderer.hideUnitPanel();
            }
        } else {
            if (units.length > 0) {
                console.log('move unit from ' + cursor + ' to ' + new_cursor);
                let firstUnit = units[0];
                moveUnit(cursor, new_cursor, firstUnit.unitType.mapType());
            }
        }
        cursor = new_cursor;

        // renderer.clearCursor();
    }

    mouseLeftIsDown = false;
    mouseRightIsDown = false;
}

function handleMouseLeave(event) {
    mouseLeftIsDown = false;
    mouseRightIsDown = false;
}

function changeUIState(newState) {
    uiState = newState;

    switch (uiState) {

        case UIState.menu:
            // images are cached, we can show the menu
            console.log('uistate > menu');
            $('#uistate-splash').hide();
            $('#uistate-menu').show();
            $('#uistate-play-game').hide();
            $('#uistate-create-game').hide();
            $('#uistate-generate').hide();
            $('#uistate-game').hide();
            $('#uistate-game-menu').hide();
            $('#uistate-options').hide();

            window.removeEventListener('beforeunload', preventExitOnReload, false);

            break;

        case UIState.playGame:
            console.log('uistate > playGame');
            $('#uistate-splash').hide();
            $('#uistate-menu').hide();
            $('#uistate-play-game').show();
            $('#uistate-create-game').hide();
            hideStartGameWarning();
            $('#uistate-generate').hide();
            $('#uistate-game').hide();
            $('#uistate-game-menu').hide();
            $('#uistate-options').hide();

            window.removeEventListener('beforeunload', preventExitOnReload, false);

            break;

        case UIState.createGame:
            console.log('uistate > createGame');
            $('#uistate-splash').hide();
            $('#uistate-menu').hide();
            $('#uistate-play-game').hide();
            $('#uistate-create-game').show();
            hideStartGameWarning();
            $('#uistate-generate').hide();
            $('#uistate-game').hide();
            $('#uistate-game-menu').hide();
            $('#uistate-options').hide();

            window.removeEventListener('beforeunload', preventExitOnReload, false);

            break;

        case UIState.generate:
            // user selected 'create', we want to show a spinner now
            console.log('uistate > generate');
            $('#uistate-splash').hide();
            $('#uistate-menu').hide();
            $('#uistate-play-game').hide();
            $('#uistate-create-game').hide();
            $('#uistate-generate').show();
            $('#uistate-game').hide();
            $('#uistate-game-menu').hide();
            $('#uistate-options').hide();

            window.removeEventListener('beforeunload', preventExitOnReload, false);

            break;

        case UIState.game:
            // map is generated, we can render it now
            console.log('uistate > game');
            $('#uistate-splash').hide();
            $('#uistate-menu').hide();
            $('#uistate-play-game').hide();
            $('#uistate-create-game').hide();
            $('#uistate-generate').hide();
            $('#uistate-game').show();
            $('#uistate-game-menu').hide();
            $('#uistate-options').hide();

            // add a popup to warn the user to leave the page
            window.addEventListener('beforeunload', preventExitOnReload);

            // Full page rendering
            renderer.render();

            $('#ui').removeClass('blurred');
            hideTurnBanner();
            break;

        case UIState.gameMenu:
            // we are inside the game but need to show the in-game menu
            console.log('uistate > game-menu');
            $('#uistate-splash').hide();
            $('#uistate-menu').hide();
            $('#uistate-play-game').hide();
            $('#uistate-create-game').hide();
            $('#uistate-generate').hide();
            $('#uistate-game').show();
            $('#uistate-game-menu').show();
            $('#uistate-options').hide();
            break;

        case UIState.options:
            console.log('uistate > options');
            $('#uistate-splash').hide();
            $('#uistate-menu').hide();
            $('#uistate-play-game').hide();
            $('#uistate-create-game').hide();
            $('#uistate-generate').hide();
            $('#uistate-game').hide();
            $('#uistate-game-menu').hide();
            $('#uistate-options').show();

            window.removeEventListener('beforeunload', preventExitOnReload, false);

            $('#ui').addClass('blurred');
            break;

        case UIState.tutorials:
            console.log('uistate > tutorials');
            $('#uistate-splash').hide();
            $('#uistate-menu').hide();
            $('#uistate-play-game').hide();
            $('#uistate-create-game').hide();
            $('#uistate-generate').hide();
            $('#uistate-game').hide();
            $('#uistate-game-menu').hide();
            $('#uistate-options').hide();

            window.removeEventListener('beforeunload', preventExitOnReload, false);

            $('#ui').addClass('blurred');
            break;

        default:
            throw new Error(uiState + ' not handled');
    }
}

function initUI() {
    // the current state is 'splash'

    // start caching images ...
    renderer.cacheImages(function() {
        // ... and switch to 'menu' state when done
        changeUIState(UIState.menu);
    });
}

let generation_check_timer;
let update_check_timer;

// to be called when you want to stop a timer
function abortGenerationTimer() {
    clearInterval(generation_check_timer);
}

function abortUpdateTimer() {
    clearInterval(update_check_timer);
}

function checkGameGeneration() {
    $.ajax({
        type:"GET",
        url: "/smarthexboard/" + game_id + "/create/status?timestamp=" + Date.now(),
        success: function(response) {
            console.log('refresh game generation status: ' + response.status + ', progress: ' + response.progress);
            // fixme: propagate progress to ui

            // $('#refresh_status').text(response.status);
            if (response.status === 'Ready') {
                abortGenerationTimer();
                loadMap(game_id);
            }
        },
        error: function(xhr, textStatus, exception) {
            if (xhr.status === 404) {
                console.error('Service not running: make run-qcluster');
            } else {
                handleError(xhr, textStatus, exception);
            }
        }
    });
}

function checkGameUpdate() {
    $.ajax({
        type:"GET",
        url: "/smarthexboard/" + game_id + "/update?timestamp=" + Date.now(),
        success: function(response) {
            console.log('update game: ' + JSON.stringify(response));
            // fixme: propagate progress to ui

            // $('#refresh_status').text(response.status);
            if (response.human_active === true) {
                fetchGameInfo();
            }
        },
        error: function(xhr, textStatus, exception) {
            handleError(xhr, textStatus, exception);
        }
    });
}

function formatDecimal(value) {
    if (value < 0) {
        return '' + (Math.round(value * 100) / 100).toFixed(1)
    } else {
        return '+' + (Math.round(value * 100) / 100).toFixed(1)
    }
}

function fetchGameInfo() {
    $.ajax({
        type:"GET",
        url: "/smarthexboard/" + game_id + "/info",
        success: function(response) {
            console.log('update game info: ' + JSON.stringify(response));

            // update game ui
            $('#turnLbl').text(response.turnYear + ', Turn ' + response.turn);

            // update human player information
            $('#scienceYieldValue').text(formatDecimal(response.human.science));
			if (response.human.currentTech != null) {
			    $('#tech_progress_title').text(response.human.currentTech);
			} else {
			    $('#tech_progress_title').text('-');
			}
			$('#cultureYieldValue').text(formatDecimal(response.human.culture));
			if (response.human.currentCivic != null) {
			    $('#civic_progress_title').text(response.human.currentCivic);
			} else {
			    $('#civic_progress_title').text('-');
			}
			$('#goldYieldValue').text(response.human.gold.toString());
			$('#goldIncomeValue').text(formatDecimal(response.human.income));
			$('#faithYieldValue').text(response.human.faith.toString());
			$('#faithIncomeValue').text(formatDecimal(0));
			$('#tourismYieldValue').text(formatDecimal(response.human.tourism));
			// 'notifications': self.notifications.notifications if self.human else [],

            hideTurnBanner();
            abortUpdateTimer();
        },
        error: function(xhr, textStatus, exception) {
            handleError(xhr, textStatus, exception);
        }
    });
}

function loadMap(game_id) {
    $.ajax({
        type:"GET",
        dataType: "json",
        url: "/smarthexboard/" + game_id + "/map",
        success: function(json_obj) {
            console.log('loaded map of game: ' + game_id);

            var mapObj = new Map();
            mapObj.fromJson(json_obj);
            console.log('map: ' + game_id + ' deserialized');
            renderer.setup(mapObj);

            // create canvas with this size
            setupCanvas(mapObj.canvasSize());

            changeUIState(UIState.game);

            /* start update status */
            update_check_timer = setInterval(checkGameUpdate, 1000);
            showTurnBanner();
        },
        error: function(xhr, textStatus, exception) {
            handleError(xhr, textStatus, exception);
        }
    });
}

function moveUnit(from_point, to_point, unit_map_type) {
    const formData = new FormData();
    formData.append('game_id', game_id);
    formData.append('unit_type', unit_map_type);
    formData.append('old_location', from_point);
    formData.append('new_location', to_point);

    const csrf_token = $('#csrf_token').text();

    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/smarthexboard/move_unit",
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin',
        data: formData,
        processData: false,
        contentType: false,
        success: function(json_obj) {
            console.log('moved unit from ' + from_point + ' to ' + to_point);
            let units = renderer.map.unitsAt(from_point);
            let unit = units.filter(unit => unit.unitType.mapType() === unit_map_type)[0];
            unit.moves = json_obj['moves'];
            unit.location = to_point;

            // full map rendering
            renderer.render();

            uiRenderer.hideUnitPanel(); // or update? the moves have changed
        },
        error: function(xhr, textStatus, exception) {
            handleError(xhr, textStatus, exception);
        }
    });
}

function foundCity(settler, cityName) {
    console.log('found city: ' + cityName + ' at ' + cursor);
    const formData = new FormData();
    formData.append('game_id', game_id);
    formData.append('city_name', cityName);
    formData.append('location', cursor.toString());

    const csrf_token = $('#csrf_token').text();

    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/smarthexboard/found_city",
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin',
        data: formData,
        processData: false,
        contentType: false,
        success: function(json_obj) {
            console.log('founded city "' + cityName + '" at ' + cursor);
            changeActionState(ActionState.none);

            let player = json_obj['player'];

            // remove unit, show city
            renderer.map.removeUnit(settler);
            renderer.map.addCityAt(cursor, cityName, player);

            // Full page rendering
            // renderer.render(cursor.x, cursor.y, 1);
            renderer.render();
            renderer.clearCursor();
        },
        error: function(xhr, textStatus, exception) {
            handleError(xhr, textStatus, exception);
            changeActionState(ActionState.none);
        }
    });
}

function disbandUnit(unit) {
    console.log('disband-unit ' + unit);
}

function changeActionState(newActionState) {
    actionState = newActionState;

    switch (actionState) {

        case ActionState.selectMeleeTarget:
            break;
        case ActionState.inputCityName:
            // console.log('input city name');
            uiRenderer.textInput('City Name', 'Please enter a name for your new city:', function (cityName) {
                // console.log('input city name: ' + cityName);
                let settler = renderer.map.unitsAt(cursor).filter(unit => unit.unitType.name === 'settler')[0];
                foundCity(settler, cityName);
            });
            break;
        case ActionState.disbandUnit:
            uiRenderer.message('Disband', 'Are you sure you want to disband this unit?', function () {
                let unit = renderer.map.unitsAt(cursor)[0];
                disbandUnit(unit);
            });
            break;
        case ActionState.none:
            uiRenderer.hideTextInput();
            break;
        default:
            console.log('action state ' + actionState + ' not handled');
    }
}

function showUnitPanel(unit, event, actions) {
    uiRenderer.unitPanel(unit, actions, function (action, action_index) {
        // console.log('unit action clicked: ' + action + ' index: ' + action_index);
        cursor = locationFromEvent(event);
        switch (action) {
            case 'ACTION_ATTACK':
                // console.log('attack action clicked');
                // @todo: select target
                changeActionState(ActionState.selectMeleeTarget);
                break;
            case 'ACTION_DISBAND':
                changeActionState(ActionState.disbandUnit);
                break;
            case 'ACTION_FOUND_CITY':
                changeActionState(ActionState.inputCityName);
                break;
            default:
                console.log('action ' + action + ' not handled');
        }
    });
}

function showTurnBanner() {
    $('#turnBanner').show();
    $('#game_button').css('background-image', 'url("/static/smarthexboard/img/globe/globe.gif")');
    console.log('showTurnBanner');
}

function hideTurnBanner() {
    $('#turnBanner').hide();
    $('#game_button').css('background-image', 'url("/static/smarthexboard/img/ui/buttons/button_generic@3x.png")');
    console.log('hideTurnBanner');
}

function showStartGameWarning(text) {
    $('#createGameWarning').text(text).show();
}

function hideStartGameWarning() {
    $('#createGameWarning').hide();
}

window.startGame = function startGame() {
    const leaderSelect = $('#leaderSelect').find(":selected").val();
    const difficultySelect = $('#difficultySelect').find(":selected").val();
    const mapTypeSelect = $('#mapTypeSelect').find(":selected").val();
    const mapSizeSelect = $('#mapSizeSelect').find(":selected").val();
    const csrf_token = $('#csrf_token').text();

    if (leaderSelect === '') {
        showStartGameWarning('Please select a Leader');
        return;
    }

    if (difficultySelect === '') {
        showStartGameWarning('Please select a Handicap');
        return;
    }

    if (mapTypeSelect === '') {
        showStartGameWarning('Please select a Map Type');
        return;
    }

    if (mapSizeSelect === '') {
        showStartGameWarning('Please select a Map Size');
        return;
    }

    hideStartGameWarning();

    const formData = new FormData();
    formData.append('leader', leaderSelect);
    formData.append('handicap', difficultySelect);
    formData.append('mapType', mapTypeSelect);
    formData.append('mapSize', mapSizeSelect);

    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/smarthexboard/create",
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin',
        data: formData,
        processData: false,
        contentType: false,
        success: function(json_obj) {
            // console.log('created game: ' + JSON.stringify(json_obj));
            console.log('created game: ' + json_obj.game_id);
            game_id = json_obj.game_id;

            changeUIState(UIState.generate);

            /* start checking status */
            generation_check_timer = setInterval(checkGameGeneration, 1000);
        },
        error: function(xhr, textStatus, exception) {
            handleError(xhr, textStatus, exception);
        }
    });
}

window.playGame = function playGame() {
    console.log('playGame');
    changeUIState(UIState.playGame);
}

window.quickGame = function quickGame() {
    const csrf_token = $('#csrf_token').text();

    const formData = new FormData();
    formData.append('leader', 'alexander');
    formData.append('handicap', 'settler');
    formData.append('mapType', 'continents');
    formData.append('mapSize', 'duel');

    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/smarthexboard/create",
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin',
        data: formData,
        processData: false,
        contentType: false,
        success: function(json_obj) {
            // console.log('created game: ' + JSON.stringify(json_obj));
            console.log('created game: ' + json_obj.game_id);
            game_id = json_obj.game_id;

            changeUIState(UIState.generate);

            /* start checking status */
            generation_check_timer = setInterval(checkGameGeneration, 1000);
        },
        error: function(xhr, textStatus, exception) {
            handleError(xhr, textStatus, exception);
        }
    });
}

window.createGame = function createGame() {
    console.log('createGame');
    changeUIState(UIState.createGame);
}

window.loadGame = function createGame() {
    console.log('loadGame');
    // changeUIState(UIState.createGame);
}

window.play = function play() {
    console.log('play');
    changeUIState(UIState.generate);
}

window.openTechDialog = function openTechDialog() {
    console.log('openTechDialog');
    $('#dialogs').show();
    $('#techs_dialog').show();
}

window.openCivicDialog = function openCivicDialog() {
    console.log('openCivicDialog');
    $('#dialogs').show();
    $('#civics_dialog').show();
}

window.openGovernmentDialog = function openGovernmentDialog() {
    console.log('openGovernmentDialog');
}

window.openReligionDialog = function openReligionDialog() {
    console.log('openReligionDialog');
}

window.openGreatPeoplesDialog = function openGreatPeoplesDialog() {
    console.log('openGreatPeoplesDialog');
}

window.openGovernorsDialog = function openGovernorsDialog() {
    console.log('openGovernorsDialog');
}

window.openMomentsDialog = function openMomentsDialog() {
    console.log('openMomentsDialog');
}

window.turnButtonClicked = function turnButtonClicked() {
    console.log('turnButtonClicked');

    abortUpdateTimer();

    $.ajax({
        type:"GET",
        dataType: "json",
        url: "/smarthexboard/" + game_id + "/turn",
        success: function(json_obj) {
            console.log('game turned: ' + game_id);
        },
        error: function(xhr, textStatus, exception) {
            handleError(xhr, textStatus, exception);
        }
    });
}

window.openGameMenu = function openGameMenu() {
    console.log('openGameMenu');
    changeUIState(UIState.gameMenu);
}

window.closeMenu = function closeMenu() {
    console.log('closeMenu');
    changeUIState(UIState.game);
}

window.exitGame = function exitGame() {
    console.log('exitGame');
    abortUpdateTimer();
    changeUIState(UIState.menu);
}

window.options = function options() {
    console.log('options');
    changeUIState(UIState.options);
}

window.quitOptions = function quitOptions() {
    console.log('quitOptions');
    changeUIState(UIState.menu);
}

window.tutorials = function tutorials() {
    console.log('tutorials');
    changeUIState(UIState.tutorials);
}

window.game_options = function tutorials() {
    console.log('options');
    // changeUIState(UIState.options);
}

window.credits = function tutorials() {
    console.log('credits');
    // changeUIState(UIState.credits);
}