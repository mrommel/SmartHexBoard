/*================
 Template Name: Datrics Data Science & Analytics HTML Template
 Description: All type of data science, artificial intelligence & machine learning template.
 Version: 1.0
 Author: MiRo
=======================*/

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

    if (renderer.texturesLoaded) {
        setupCanvas();

        // Full page rendering
        renderer.render();
    } else {
        throw new Error('no textures loaded');
    }
}

function setupCanvas() {
    // get the canvas
    var terrainsCanvas = document.getElementById('terrains');

    terrainsCanvas.width = window.innerWidth;
    terrainsCanvas.height = window.innerHeight;

    var resourcesCanvas = document.getElementById('resources');

    resourcesCanvas.width = window.innerWidth;
    resourcesCanvas.height = window.innerHeight;

    var featuresCanvas = document.getElementById('features');

    featuresCanvas.width = window.innerWidth;
    featuresCanvas.height = window.innerHeight;

    document.getElementById('game').style.width = window.innerWidth + "px";
    document.getElementById('game').style.height = window.innerHeight + "px";

    // attach mouse events
    var vp = document.getElementById('game');
    vp.addEventListener("mousedown", handleMouseDown, true);
    vp.addEventListener("mousemove", handleMouseMove, true);
    vp.addEventListener("mouseup", handleMouseUp, true);
}

function getMouseInfo(canvas, e) {
	var mx, my, right_click;
	var viewport = document.getElementById("terrains");
	if (e.which) right_click = (e.which == 3);
	else if (e.button) right_click = (e.button == 2);

	mx = e.pageX - canvas.offsetLeft - viewport.clientLeft - viewport.offsetLeft + viewport.scrollLeft;
	my = e.pageY - canvas.offsetTop - viewport.clientTop - viewport.offsetTop + viewport.scrollTop;

	return new MouseInfo(mx, my, right_click);
}

function handleMouseDown(event) {
    mouse.x = event.pageX;
    mouse.Y = event.pageY;
    mouseIsDown = true;

    var vp = document.getElementById('terrains');
    offset.x = vp.offsetLeft - event.clientX;
    offset.y = vp.offsetTop - event.clientY;

    // Get the canvas element form the page
    var terrainCanvas = document.getElementById('terrains');

    var minfo = getMouseInfo(terrainCanvas, event);
	// var cell = renderer.screenToCell(minfo.x, minfo.y);
	var screenPoint = new CGPoint(minfo.x, minfo.y);
	var cell = new HexPoint(screenPoint);

    // var text = 'mouse click on: ' + cell.x + ', ' + cell.y;
    // console.log(text);
    // uiRenderer.message('mouse clicked', text);
}

function handleMouseMove(event) {
    event.preventDefault();
	mouse.x = event.pageX;
    mouse.Y = event.pageY;
    // console.log('mouse move: ' + mouse.x + ', ' + mouse.y + ' mouseIsDown=' + mouseIsDown);

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

function changeUIState(newState) {
    uiState = newState;

    if (uiState == UIState.menu) {
        // images are cached, we can show the menu
        console.log('uistate > menu');
        $('#uistate-splash').hide();
        $('#uistate-menu').show();
        $('#uistate-generate').hide();
        $('#uistate-game').hide();
    }

    if (uiState == UIState.generate) {
        // user selected 'play', we can generate a map now
        console.log('uistate > generate');
        $('#uistate-splash').hide();
        $('#uistate-menu').hide();
        $('#uistate-generate').show();
        $('#uistate-game').hide();

        var options = new MapOptions();
        var generator = new MapGenerator(options);

        generator.generate(function(text, progress, mapObj) {

            console.log(text);
            if (progress == 1.0) {
                // update the map
                renderer.map = mapObj;

                setupCanvas();

                changeUIState(UIState.game);
            }
        });
    }

    if (uiState == UIState.game) {
        // map is generated, we can render it now
        console.log('uistate > game');
        $('#uistate-splash').hide();
        $('#uistate-menu').hide();
        $('#uistate-generate').hide();
        $('#uistate-game').show();

        // Full page rendering
        renderer.render();

        $('#ui').removeClass('blurred');
    }
}

function initUI() {

    // current state is splash

    // start caching images
    renderer.cacheTerrainImages(function() {
        renderer.texturesLoaded = true;
        changeUIState(UIState.menu);
    });


    // makeVisible('ui-message');
    // uiRenderer.message('abc', 'def');

    /*$('#uiokbut').click(function (event) {
        event.preventDefault();

        makeHidden('ui-message');
    });
    $('#menuGame').click(function (event) {
        event.preventDefault();

        uiRenderer.message('menu', 'game');
    });*/
}

window.play = function play() {
    changeUIState(UIState.generate);
}

window.openTechDialog = function openTechDialog() {
    console.log('openTechDialog');
}

window.openCivicDialog = function openCivicDialog() {
    console.log('openCivicDialog');
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
