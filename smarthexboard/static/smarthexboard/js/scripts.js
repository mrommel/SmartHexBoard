/*================
 Template Name: Datrics Data Science & Analytics HTML Template
 Description: All type of data science, artificial intelligence & machine learning template.
 Version: 1.0
 Author: MiRo
=======================*/

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
var renderer;
var uiRenderer = new UIBuilder();

function resizeCanvas() {
    drawMap();
}

function drawMap() {
    var map = {};
    map.rows = 10;
    map.cols = 10;

    renderer = new Renderer(map);

    renderer.cacheImages(function() {
        setupCanvas();
        renderer.render();  // Full page rendering
        // renderer.render(ctx, 8, 2, 0);
        // renderer.render(ctx, 2, 8, 0);
    });
}

function setupCanvas() {
    // get the canvas
    var terrainCanvas = document.getElementById('terrains');

    terrainCanvas.width = window.innerWidth;
    terrainCanvas.height = window.innerHeight;

    // attach mouse events
    terrainCanvas.addEventListener("mousedown", handleMouseClick, false);
    terrainCanvas.addEventListener("mousemove", handleMouseMove, false);
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

function handleMouseClick(e) {
    mouse.x = e.pageX;
    mouse.Y = e.pageY;

    // Get the canvas element form the page
    var terrainCanvas = document.getElementById('terrains');

    var minfo = getMouseInfo(terrainCanvas, e);
	var cell = renderer.screenToCell(minfo.x, minfo.y);

    var text = 'mouse click on: ' + cell.col + ', ' + cell.row;
    console.log(text);
    uiRenderer.message('mouse clicked', text);
}

function handleMouseMove(e) {
	mouse.x = e.pageX;
    mouse.Y = e.pageY;
    // console.log('mouse move: ' + mouse.x + ', ' + mouse.y);
}

function initUI() {
    // makeVisible('ui-message');
    // uiRenderer.message('abc', 'def');

    /*$('#uiokbut').click(function (event) {
        event.preventDefault();

        makeHidden('ui-message');
    });*/
}