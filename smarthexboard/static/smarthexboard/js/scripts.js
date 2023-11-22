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

        // add a popup to warn the user to leave the page
        window.addEventListener('beforeunload', (event) => {
          // Cancel the event as stated by the standard.
          event.preventDefault();
          // Chrome requires returnValue to be set.
          event.returnValue = '';
        });
    });
}); // JQuery end

var mouse = { x: 0, y: 0 };
var mouseIsDown = false;
var offset = { x: 0, y: 0 };

var renderer = new Renderer(null);
var uiRenderer = new UIBuilder();
var uiState = UIState.Splash;

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
        console.log('textures not initialzed yet');
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

    document.getElementById('game').style.width = window.innerWidth + "px";
    document.getElementById('game').style.height = window.innerHeight + "px";

    // attach mouse events
    var vp = document.getElementById('game');
    vp.addEventListener("mousedown", handleMouseDown, true);
    vp.addEventListener("mousemove", handleMouseMove, true);
    vp.addEventListener("mouseup", handleMouseUp, true);
    vp.addEventListener("mouseleave", handleMouseLeave, true);
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
    mouse.x = event.pageX;
    mouse.Y = event.pageY;
    mouseIsDown = true;

    var vp = document.getElementById('terrains');
    offset.x = vp.offsetLeft - event.clientX;
    offset.y = vp.offsetTop - event.clientY;
}

function handleMouseMove(event) {
    event.preventDefault();
	mouse.x = event.pageX;
    mouse.Y = event.pageY;
    // console.log('mouse move: ' + mouse.x + ', ' + mouse.y + ' mouseIsDown=' + mouseIsDown);

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
    my = canvasSize.height - (my + canvasOffset.y) - canvasOffset.y;

    var point_on_canvas = new CGPoint(mx, my);
    // var screen_position = new CGPoint(event.clientX - canvas.offsetLeft, (event.clientY - canvas.offsetTop));
    var screen_position = new CGPoint(mx, my);
    var map_position = new HexPoint(screen_position);

    var terrainText = '<invalid>';
    var hillsText = ' (no hills)';
    var climateZoneText = '<invalid>';
    var resourceText = '<invalid>';
    if (renderer.map.valid(map_position)) {
        terrainText = renderer.map.terrainAt(map_position);
        if (renderer.map.isHillsAt(map_position)) {
            hillsText = ' (has hills)';
        }
        climateZoneText = renderer.map.climateZoneAt(map_position);
        resourceText = renderer.map.resourceAt(map_position);
    } else {
        terrainText = '';
        hillsText = '';
        climateZoneText = '';
        resourceText = '';
    }

    var tooltipSpan = document.getElementById('tooltip');
    var x = event.clientX, y = event.clientY;
    tooltipSpan.style.top = (y + 20) + 'px';
    tooltipSpan.style.left = (x + 0) + 'px';
    tooltipSpan.style.display = 'block';
    tooltipSpan.innerHTML = 'point: ' + map_position + '<br />' + terrainText + hillsText + '<br />' + resourceText + '<br />' + climateZoneText; // + '<br />' + point_on_canvas;

    if (mouseIsDown) {
        var terrains = document.getElementById('terrains');
        terrains.style.left = (event.clientX + offset.x) + 'px';
        terrains.style.top  = (event.clientY + offset.y) + 'px';

        var features = document.getElementById('features');
        features.style.left = (event.clientX + offset.x) + 'px';
        features.style.top  = (event.clientY + offset.y) + 'px';

        var resources = document.getElementById('resources');
        resources.style.left = (event.clientX + offset.x) + 'px';
        resources.style.top  = (event.clientY + offset.y) + 'px';

        // console.log('move: x=' + vp.style.left + ' y=' + vp.style.top);
    }
}

function handleMouseUp(event) {
    mouseIsDown = false;
}

function handleMouseLeave(event) {
    mouseIsDown = false;
}

function changeUIState(newState) {
    uiState = newState;

    switch (uiState) {

        case UIState.menu:
            // images are cached, we can show the menu
            console.log('uistate > menu');
            $('#uistate-splash').hide();
            $('#uistate-menu').show();
            $('#uistate-create-game').hide();
            $('#uistate-generate').hide();
            $('#uistate-game').hide();
            $('#uistate-game-menu').hide();
            $('#uistate-options').hide();
            break;

        case UIState.createGame:
            console.log('uistate > createGame');
            $('#uistate-splash').hide();
            $('#uistate-menu').hide();
            $('#uistate-create-game').show();
            hideStartGameWarning();
            $('#uistate-generate').hide();
            $('#uistate-game').hide();
            $('#uistate-game-menu').hide();
            $('#uistate-options').hide();
            break;

        case UIState.generate:
            // user selected 'play', we can generate a map now
            console.log('uistate > generate');
            $('#uistate-splash').hide();
            $('#uistate-menu').hide();
            $('#uistate-create-game').hide();
            $('#uistate-generate').show();
            $('#uistate-game').hide();
            $('#uistate-game-menu').hide();
            $('#uistate-options').hide();

            startMapGeneration();
            break;

        case UIState.game:
            // map is generated, we can render it now
            console.log('uistate > game');
            $('#uistate-splash').hide();
            $('#uistate-menu').hide();
            $('#uistate-create-game').hide();
            $('#uistate-generate').hide();
            $('#uistate-game').show();
            $('#uistate-game-menu').hide();
            $('#uistate-options').hide();

            // Full page rendering
            renderer.render();

            $('#ui').removeClass('blurred');
            break;

        case UIState.gameMenu:
            // we are inside the game but need to show the in-game menu
            console.log('uistate > game-menu');
            $('#uistate-splash').hide();
            $('#uistate-menu').hide();
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
            $('#uistate-create-game').hide();
            $('#uistate-generate').hide();
            $('#uistate-game').hide();
            $('#uistate-game-menu').hide();
            $('#uistate-options').show();

            $('#ui').addClass('blurred');
            break;

        case UIState.tutorials:
            console.log('uistate > tutorials');
            $('#uistate-splash').hide();
            $('#uistate-menu').hide();
            $('#uistate-create-game').hide();
            $('#uistate-generate').hide();
            $('#uistate-game').hide();
            $('#uistate-game-menu').hide();
            $('#uistate-options').hide();

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

function startMapGeneration() {
    // reset map_uuid
    map_uuid = '';

    $.ajax({
        type:"GET",
        url: "/smarthexboard/generate_map/DUEL/CONTINENTS/",
        success: function(response) {
            map_uuid = response.uuid;
            console.log('started generating map ' + map_uuid);

            /* start checking status */
            generation_check_timer = setInterval(checkGameGeneration, 1000);
        },
        error: function(xhr, textStatus, exception) {
            handleError(xhr, textStatus, exception);
        }
    });
}

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
            console.log('refresh game update: ' + response.status + ', progress: ' + response.progress);
            console.log('update game: ' + JSON.stringify(response));
            // fixme: propagate progress to ui

            // $('#refresh_status').text(response.status);
            if (response.status == 'Ready') {

            }
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

            var canvasSize = mapObj.canvasSize();
            // create canvas with this size
            setupCanvas(canvasSize);

            changeUIState(UIState.game);

            /* start update status */
            update_check_timer = setInterval(checkGameUpdate, 1000);
        },
        error: function(xhr, textStatus, exception) {
            handleError(xhr, textStatus, exception);
        }
    });
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
    // console.log('leader: ' + leaderSelect);
    var difficultySelect = $('#difficultySelect').find(":selected").val();
    // console.log('handicap: ' + difficultySelect);
    var mapTypeSelect = $('#mapTypeSelect').find(":selected").val();
    // console.log('mapType: ' + mapTypeSelect);
    var mapSizeSelect = $('#mapSizeSelect').find(":selected").val();
    // console.log('mapSize: ' + mapSizeSelect);
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