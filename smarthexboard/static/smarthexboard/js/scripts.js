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

    // make canvas full screen
    $(document).ready(function () {
        drawMap();

        initUI();

        // hide pre-loader
        $('#preloader').delay(200).fadeOut('fade');
    });

}); // JQuery end

var mouse = { x: 0, y: 0 };
var mouseIsDown = false;
var offset = { x: 0, y: 0 };

var renderer;
var uiRenderer = new UIBuilder();
var map = null;

/**
 * Preloads the image, and invokes the callback as soon
 * as the image is loaded.
 * https://gist.github.com/enyo/5697533

function preload(src, callback) {
    // Create a temporary image.
    var img = new Image();

    // Invoke the callback as soon as the image is loaded
    // Has to be set **before** the .src attribute. Otherwise
    // `onload` could fire before the handler is set.
    $(img).load(callback);

    img.src = src;
};*/

function resizeCanvas() {
    drawMap();
}

function drawMap() {

    renderer = new Renderer(map);

    renderer.cacheTerrainImages(function() {
        setupCanvas();

        var options = new MapOptions();
        var generator = new MapGenerator(options);

        generator.generate(function(text, progress, mapObj) {

            console.log(text);
            if (progress == 1.0) {
                // keep the map
                map = mapObj;
                renderer.map = mapObj;

                // Full page rendering
                renderer.render();
                // renderer.render(ctx, 8, 2, 0);
                // renderer.render(ctx, 2, 8, 0);
            }
        });
    });
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

    // attach mouse events
    var vp = document.getElementById('game');
    vp.addEventListener("mousedown", handleMouseDown, true);
    vp.addEventListener("mousemove", handleMouseMove, true);
    vp.addEventListener("mouseup", handleMouseUp, true);
}

function getMouseInfo(canvas, e) {
	var mx, my, right_click;
	var viewport = document.getElementById("game");
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

    var vp = document.getElementById('game');
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
        var vp = document.getElementById('game');
        vp.style.left = (event.clientX + offset.x) + 'px';
        vp.style.top  = (event.clientY + offset.y) + 'px';

        // console.log('move: x=' + vp.style.left + ' y=' + vp.style.top);
    }
}

function handleMouseUp(event) {
    mouseIsDown = false;
}

function initUI() {
    // makeVisible('ui-message');
    // uiRenderer.message('abc', 'def');

    /*$('#uiokbut').click(function (event) {
        event.preventDefault();

        makeHidden('ui-message');
    });*/
    $('#menuGame').click(function (event) {
        event.preventDefault();

        uiRenderer.message('menu', 'game');
    });
}