/*================
 Template Name: Datrics Data Science & Analytics HTML Template
 Description: All type of data science, artificial intelligence & machine learning template.
 Version: 1.0
 Author: MiRo
=======================*/

import { MouseInfo, CGPoint } from './base/prototypes.js';
import { HexPoint } from './base/point.js';
import { TerrainTypes, FeatureTypes, ResourceTypes } from './map/types.js';
import { Map } from './map/map.js';
import { MapOptions, MapGenerator } from './map/generator.js';
import { Renderer } from './renderer.js';

// TABLE OF CONTENTS
// 1. preloader
// 2. canvas full screen

jQuery(function ($) {

    'use strict';

    $(document).ready(function () {
        initUI();
    });
}); // JQuery end

var mouse = { x: 0, y: 0 };
var mouseLeftIsDown = false;
var mouseRightIsDown = false;
var offset = { x: 0, y: 0 };
var cursor = new HexPoint(0, 0);

var renderer = new Renderer(null);
var uiRenderer = new UIBuilder();
var uiState = UIState.Splash;

function preventExitOnReload(event) {
    // Cancel the event as stated by the standard.
    event.preventDefault();
    // Chrome requires returnValue to be set.
    event.returnValue = '';
}

window.resizeCanvas = function resizeCanvas() {
    if (uiState == UIState.game) {
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
    var terrainsCanvas = document.getElementById('terrains');
    terrainsCanvas.width = canvasSize.width;
    terrainsCanvas.height = canvasSize.height;

    var resourcesCanvas = document.getElementById('resources');
    resourcesCanvas.width = canvasSize.width;
    resourcesCanvas.height = canvasSize.height;

    var featuresCanvas = document.getElementById('features');
    featuresCanvas.width = canvasSize.width;
    featuresCanvas.height = canvasSize.height;

    var unitsCanvas = document.getElementById('units');
    unitsCanvas.width = canvasSize.width;
    unitsCanvas.height = canvasSize.height;

    var cursorCanvas = document.getElementById('cursor');
    cursorCanvas.width = canvasSize.width;
    cursorCanvas.height = canvasSize.height;

    document.getElementById('game').style.width = window.innerWidth + "px";
    document.getElementById('game').style.height = window.innerHeight + "px";

    // attach mouse events
    var vp = document.getElementById('game');
    vp.addEventListener("mousedown", handleMouseDown, true);
    vp.addEventListener("mousemove", handleMouseMove, true);
    vp.addEventListener("mouseup", handleMouseUp, true);
    vp.addEventListener("mouseleave", handleMouseLeave, true);

    document.addEventListener('contextmenu', function(event) {
        event.preventDefault();
    }, true);
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

function handleMouseDown(event) {
    var leftButtonDown = (event.which == 1);
    var rightButtonDown = (event.which == 3);
    var viewport = document.getElementById('game');
    var canvas = document.getElementById('terrains');
    offset.x = canvas.offsetLeft - event.clientX;
    offset.y = canvas.offsetTop - event.clientY;

    var mx = event.pageX - canvas.offsetLeft - viewport.clientLeft - viewport.offsetLeft + viewport.scrollLeft;
	var my = event.pageY - canvas.offsetTop - viewport.clientTop - viewport.offsetTop + viewport.scrollTop;

    var canvasSize = renderer.map.canvasSize();
    var canvasOffset = renderer.map.canvasOffset();

    mx = mx - canvasOffset.x;
    my = my - canvasOffset.y;
    my = canvasSize.height - (my + canvasOffset.y) - canvasOffset.y + 30;

    var point_on_canvas = new CGPoint(mx, my);
    var screen_position = new CGPoint(mx, my);
    var new_cursor = new HexPoint(screen_position);
    if (rightButtonDown && (new_cursor.x != cursor.x || new_cursor.y != cursor.y)) {
        event.preventDefault();
        cursor = new_cursor;
        renderer.renderCursor(cursor);

        mouse.x = event.pageX;
        mouse.y = event.pageY;
        rightButtonDown = true;
    }

    if (leftButtonDown) {
        mouseLeftIsDown = true;
        // console.log('cursor set to: ' + cursor);
    }
}

function handleMouseMove(event) {
    event.preventDefault();
	mouse.x = event.pageX;
    mouse.Y = event.pageY;
    // console.log('mouse move: ' + mouse.x + ', ' + mouse.y + ' mouseLeftIsDown=' + mouseLeftIsDown);

    var viewport = document.getElementById('game');
    var canvas = document.getElementById('terrains');

    var mx = event.pageX - canvas.offsetLeft - viewport.clientLeft - viewport.offsetLeft + viewport.scrollLeft;
	var my = event.pageY - canvas.offsetTop - viewport.clientTop - viewport.offsetTop + viewport.scrollTop;

    var canvasSize = renderer.map.canvasSize();
    var canvasOffset = renderer.map.canvasOffset();

    // screen.y = canvasSize.height - (screen.y + canvasOffset.y) - canvasOffset.y;
    // console.log('screen=' + screen);
    // screen.x + canvasOffset.x, screen.y + canvasOffset.y
    mx = mx - canvasOffset.x;
    my = my - canvasOffset.y;
    my = canvasSize.height - (my + canvasOffset.y) - canvasOffset.y + 30;

    var point_on_canvas = new CGPoint(mx, my);
    // var screen_position = new CGPoint(event.clientX - canvas.offsetLeft, (event.clientY - canvas.offsetTop));
    var screen_position = new CGPoint(mx, my);
    var map_position = new HexPoint(screen_position);

    var terrainText = '<invalid>';
    var hillsText = ' (no hills)';
    var climateZoneText = '<invalid>';
    var resourceText = '<invalid>';
    var unitsText = '[]';

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

    var tooltipSpan = document.getElementById('tooltip');
    var x = event.clientX, y = event.clientY;
    tooltipSpan.style.top = (y + 20) + 'px';
    tooltipSpan.style.left = (x + 0) + 'px';
    tooltipSpan.style.display = 'block';
    tooltipSpan.innerHTML = 'point: ' + map_position + '<br />' + terrainText + hillsText + '<br />' + resourceText + '<br />' + climateZoneText + '<br />' + unitsText;

    if (mouseLeftIsDown) {
        var terrainsCanvas = document.getElementById('terrains');
        terrainsCanvas.style.left = (event.clientX + offset.x) + 'px';
        terrainsCanvas.style.top  = (event.clientY + offset.y) + 'px';

        var featuresCanvas = document.getElementById('features');
        featuresCanvas.style.left = (event.clientX + offset.x) + 'px';
        featuresCanvas.style.top  = (event.clientY + offset.y) + 'px';

        var resourcesCanvas = document.getElementById('resources');
        resourcesCanvas.style.left = (event.clientX + offset.x) + 'px';
        resourcesCanvas.style.top  = (event.clientY + offset.y) + 'px';

        var unitsCanvas = document.getElementById('units');
        unitsCanvas.style.left = (event.clientX + offset.x) + 'px';
        unitsCanvas.style.top  = (event.clientY + offset.y) + 'px';

        var cursorCanvas = document.getElementById('cursor');
        cursorCanvas.style.left = (event.clientX + offset.x) + 'px';
        cursorCanvas.style.top  = (event.clientY + offset.y) + 'px';
        // console.log('move: x=' + vp.style.left + ' y=' + vp.style.top);
    }
}

function handleMouseUp(event) {
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

    // current state is splash

    // start caching images
    renderer.cacheImages(function() {
        changeUIState(UIState.menu);
    });
}

function handleError(xhr, textStatus, exception) {

    if (xhr.status === 0) {
        console.log('Not connect.\n Verify Network.');
    } else if (xhr.status == 404) {
        // 404 page error
        console.log('Requested page not found. [404]');
    } else if (xhr.status == 500) {
        // 500 Internal Server error
        console.log('Internal Server Error [500].');
    } else if (exception === 'parsererror') {
        // Requested JSON parse
        console.log('Requested JSON parse failed.');
    } else if (exception === 'timeout') {
        // Time out error
        console.log('Time out error.');
    } else if (exception === 'abort') {
        // request aborted
        console.log('Ajax request aborted.');
    } else {
        console.log('Uncaught Error.\n' + xhr.responseText);
    }
}

var generation_check_timer;
var update_check_timer;
var game_uuid;

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
        url: "/smarthexboard/game/" + game_uuid + "/create/status?timestamp=" + Date.now(),
        success: function(response) {
            console.log('refresh game generation status: ' + response.status + ', progress: ' + response.progress);
            // fixme: propagate progress to ui

            // $('#refresh_status').text(response.status);
            if (response.status == 'Ready') {
                abortGenerationTimer();
                loadMap(game_uuid);
            }
        },
        error: function(xhr, textStatus, exception) {
            handleError(xhr, textStatus, exception);
        }
    });
}

function checkGameUpdate() {
    $.ajax({
        type:"GET",
        url: "/smarthexboard/game/" + game_uuid + "/update?timestamp=" + Date.now(),
        success: function(response) {
            // console.log('update game: ' + JSON.stringify(response));
            // fixme: propagate progress to ui

            // $('#refresh_status').text(response.status);
            if (response.human_active == true) {
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
        url: "/smarthexboard/game/" + game_uuid + "/info",
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

function loadMap(game_uuid) {

    $.ajax({
        type:"GET",
        dataType: "json",
        url: "/smarthexboard/game/" + game_uuid + "/map",
        success: function(json_obj) {
            console.log('loaded map of game: ' + game_uuid);

            var mapObj = new Map();
            mapObj.fromJson(json_obj);
            console.log('map: ' + game_uuid + ' deserialized');
            renderer.map = mapObj;

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
    $('#createGameWarning').text(text);
    $('#createGameWarning').show();
}

function hideStartGameWarning() {
    $('#createGameWarning').hide();
}

window.startGame = function startGame() {
    var leaderSelect = $('#leaderSelect').find(":selected").val();
    var difficultySelect = $('#difficultySelect').find(":selected").val();
    var mapTypeSelect = $('#mapTypeSelect').find(":selected").val();
    var mapSizeSelect = $('#mapSizeSelect').find(":selected").val();
    var csrf_token = $('#csrf_token').text()

    if (leaderSelect == '') {
        showStartGameWarning('Please select a Leader');
        return;
    }

    if (difficultySelect == '') {
        showStartGameWarning('Please select a Handicap');
        return;
    }

    if (mapTypeSelect == '') {
        showStartGameWarning('Please select a Map Type');
        return;
    }

    if (mapSizeSelect == '') {
        showStartGameWarning('Please select a Map Size');
        return;
    }

    hideStartGameWarning();

    var formData = new FormData();
    formData.append('leader', leaderSelect);
    formData.append('handicap', difficultySelect);
    formData.append('mapType', mapTypeSelect);
    formData.append('mapSize', mapSizeSelect);

    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/smarthexboard/game/create",
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin',
        data: formData,
        processData: false,
        contentType: false,
        success: function(json_obj) {
            // console.log('created game: ' + JSON.stringify(json_obj));
            console.log('created game: ' + json_obj.game_uuid);
            game_uuid = json_obj.game_uuid;

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
    var csrf_token = $('#csrf_token').text()

    var formData = new FormData();
    formData.append('leader', 'alexander');
    formData.append('handicap', 'settler');
    formData.append('mapType', 'continents');
    formData.append('mapSize', 'duel');

    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/smarthexboard/game/create",
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin',
        data: formData,
        processData: false,
        contentType: false,
        success: function(json_obj) {
            // console.log('created game: ' + JSON.stringify(json_obj));
            console.log('created game: ' + json_obj.game_uuid);
            game_uuid = json_obj.game_uuid;

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
        url: "/smarthexboard/game/" + game_uuid + "/turn",
        success: function(json_obj) {
            console.log('game turned: ' + game_uuid);
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