/**
 * Renderer - draws the graphic elements on canvases
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

import { TerrainTypes, FeatureTypes, ResourceTypes } from './map/types.js';
import { Map } from './map/map.js';

function Renderer() {

    // Hex sizes compatible with PG2 sizes
	this.s = 36;  // hexagon segment size                    |\
	this.h = this.s * 0.5; // hexagon height h = sin(30)*s           r| \ s
	this.r = this.s * 0.64;  // hexagon radius r = s*0.833  -h-

	// Canvas offset from the browser window (leaves space for top menu)
	this.canvasOffsetX = 0;
	this.canvasOffsetY = 0;

	// Where to start rendering respective to the canvas
	// Since PG2 maps define even the half and "quarter" hexes that form at the edges we need to offset those
	this.renderOffsetX = 50 - (this.s + this.h);
	this.renderOffsetY = 50 - this.r;

	// we slice the screen in columns of s + h size
	this.colSlice = this.s + this.h;
	// add an offset for better rounding of mouse position in a column
	this.mousePrecisionOffset = this.s/100;

	// canvases and contexts
	this.terrainsCanvas = null;
	this.terrainsCtx = null;
	this.resourcesCanvas = null;
	this.resourcesCtx = null;

	// image cache dicts
	this.imgTerrains = {};
	this.imgResources = {};
	this.imgFeatures = {};
	this.texturesLoaded = false;

    // Check if the canvases already exists in the current document to prevent
    // overlaying multiple rendering instances
    if ((this.terrainsCanvas = document.getElementById('terrains')) === null) {
        this.terrainsCanvas = addTag('game', 'canvas');
    }
    this.terrainsCanvas.id = "terrains";
    this.terrainsCtx = this.terrainsCanvas.getContext('2d');
    console.log('terrain canvas created');

    if ((this.featuresCanvas = document.getElementById('features')) === null) {
        this.featuresCanvas = addTag('game', 'canvas');
    }
    this.featuresCanvas.id = "features";
    this.featuresCtx = this.featuresCanvas.getContext('2d');
    console.log('features canvas created');

    if ((this.resourcesCanvas = document.getElementById('resources')) === null) {
        this.resourcesCanvas = addTag('game', 'canvas');
    }
    this.resourcesCanvas.id = "resources";
    this.resourcesCtx = this.resourcesCanvas.getContext('2d');
    console.log('resource canvas created');

    // canvasOffsetX = window.innerWidth/2 - imgMapBackground.width/2;
    if (this.canvasOffsetX < 0) { this.canvasOffsetX = 0; }

    // Center the canvases
    this.terrainsCanvas.style.cssText = 'z-index: 0; position: absolute; left: ' + this.canvasOffsetX +'px; top:' + this.canvasOffsetY + 'px;';
    this.resourcesCanvas.style.cssText = 'z-index: 1; position: absolute; left: ' + this.canvasOffsetX +'px; top:' + this.canvasOffsetY + 'px;';
    this.featuresCanvas.style.cssText = 'z-index: 2; position: absolute; left: ' + this.canvasOffsetX +'px; top:' + this.canvasOffsetY + 'px;';

    // Set the width/height of the container div to browser window width/height
    // This improves the performance. User will scroll the div instead of window
    document.getElementById('game').style.width = window.innerWidth + "px";
    document.getElementById('game').style.height = window.innerHeight + "px";
    document.getElementById('game').tabIndex = 1; // For focusing the game area
    document.getElementById('game').focus();
}

Renderer.prototype.render = function(orow, ocol, range) {

    // console.log('==> render tile at: ' + ocol + ', ' + orow);

    // the map (cell) coords that will be cleared by clearRect
    var clearZone = this.getZoneRangeLimits(orow, ocol, range + 1);
    // the map (cell) coords that will be rendered hex by hex
    var renderZone = this.getZoneRangeLimits(orow, ocol, range + 2);

    var spos = this.cellToScreen(clearZone.srow, clearZone.scol, false);
    var epos = this.cellToScreen(clearZone.erow, clearZone.ecol, false);

    this.terrainsCanvas = document.getElementById('terrains');
    this.terrainsCtx = this.terrainsCanvas.getContext('2d');
    this.terrainsCtx.clearRect(spos.x, spos.y, epos.x - spos.x, epos.y - spos.y);

    this.resourcesCanvas = document.getElementById('resources');
    this.resourcesCtx = this.resourcesCanvas.getContext('2d');
    this.resourcesCtx.clearRect(spos.x, spos.y, epos.x - spos.x, epos.y - spos.y);

    // console.log('render x=' + renderZone.srow + ' - ' + renderZone.erow);
    for (var row = renderZone.srow; row < renderZone.erow; row++) {
        // we space the hexagons on each line next column being on the row below
        for (var col = renderZone.scol; col < renderZone.ecol; col++) {

            // hex = map.map[row][col];
            var hex = new HexPoint(col, row);
            // console.log('hex=' + hex);
            var screen = hex.toScreen();
            // console.log('screen=' + screen);

            var terrain = this.map.terrainAt(hex);
            // console.log('terrain=' + terrain + ', at=' + hex);
            var img = this.imgTerrains[terrain.texture];
            // console.log('img=' + img);
            this.terrainsCtx.drawImage(img, screen.x, screen.y, 72, 72);
            // console.log('render tile at: ' + col + ', ' + row + ' => ' + x0 + ', ' + y0);

            var feature = this.map.featureAt(hex);
            if (feature !== FeatureTypes.none) {
                // console.log('feature=' + feature + ', at=' + hex);
                var index = Math.abs(hex.x + hex.y) % feature.textures.length;
                var textureName = feature.textures[index];
                var img = this.imgFeatures[textureName];
                this.resourcesCtx.drawImage(img, screen.x, screen.y, 72, 72);
            }

            var resource = this.map.resourceAt(hex);
            if (resource !== ResourceTypes.none) {
                // console.log('resource=' + resource + ', at=' + hex);
                var img = this.imgResources[resource.texture];
                this.resourcesCtx.drawImage(img, screen.x, screen.y, 72, 72);
            }
        }
    }
}

// Returns min and max row,col for a range around a cell(row,col)
Renderer.prototype.getZoneRangeLimits =	function(row, col, range) {
    var z = { srow: 0, scol: 0, erow: this.map.rows, ecol: this.map.cols };

    if (row === null || col === null)
        row = col = 0;

    if (range !== null && range >= 0) {
        z.srow = row - range;
        z.scol = col - range;
        z.erow = row + range;
        z.ecol = col + range;

        if (z.srow < 0) z.srow = 0;
        if (z.scol < 0) z.scol = 0;
        if (z.erow > map.rows) z.erow = map.rows;
        if (z.ecol > map.cols) z.ecol = map.cols;
    } else {
        // if (logRenderSpeed) console.log("Full zone canvas render");
    }

    // console.log('getZoneRangeLimits(' + col + ', ' + row + ', ' + range + ')');
    // console.log('   ==> (' + z.scol + ' - ' + z.ecol + ' | ' + z.srow + ' - ' + z.erow + ')');

    return z;
}

// Returns the top corner position of a hex in screen coordinates relative to canvas
// if absolute is set canvas offsets are added to positions
Renderer.prototype.cellToScreen = function(row, col, absolute) {
    var x0, y0;

    if (col & 1) { // odd column
        y0 =  row * 2 * this.r + this.r + this.renderOffsetY;
        x0 =  col * (this.s + this.h) + this.h + this.renderOffsetX;
    } else {
        y0 = row * 2 * this.r  + this.renderOffsetY;
        x0 = col * (this.s + this.h) + this.h + this.renderOffsetX;
    }

    if (absolute) {
        var vp = document.getElementById('game');
        x0 += this.canvasOffsetX - vp.clientLeft - vp.offsetLeft;
        y0 += this.canvasOffsetY - vp.clientTop - vp.offsetTop;
    }

    return new CGPoint(x0, y0);
}

// Converts from screen x,y to row,col in map array
Renderer.prototype.screenToCell = function(x, y) {
    var vrow; // virtual graphical rows
    var trow, tcol; // true map rows/cols

    tcol = Math.round((x - this.renderOffsetX) / this.colSlice + this.mousePrecisionOffset) - 1;
    // console.log(tcol);
    // a graphical row (half hex) not the array row
    vrow = (y - this.renderOffsetY * (~tcol & 1)) / this.r; // Half hexes add r if col is odd
    // shift to correct row index
    trow = Math.round(vrow/2 - 1 * (vrow & 1));
    if (trow < 0) { trow = 0; }
    if (trow > this.map.rows - 1) trow = this.map.rows - 1;
    if (tcol > this.map.cols - 1) tcol = this.map.cols - 1;
    return new Cell(trow, tcol);
}

// Caches images, func a function to call upon cache completion
Renderer.prototype.cacheTerrainImages = function(callbackFunction) {
	var imgList = [];
	Object.values(TerrainTypes).forEach(terrainType => {
	    imgList.push(terrainType.texture);
	});
	Object.values(FeatureTypes).forEach(featureType => {
	    featureType.textures.forEach(featureTexture => {
	        imgList.push(featureTexture);
	    });
	});
	Object.values(ResourceTypes).forEach(resourceType => {
	    imgList.push(resourceType.texture);
	});

    var loaded = 0;
    var toLoad = Object.keys(imgList).length;

    console.log('start caching ' + toLoad + ' images');

    for (var i in imgList) {
        var imgName = imgList[i];

        if (imgName.startsWith('terrain_')) {
            if (typeof this.imgTerrains[imgName] !== "undefined") {
                loaded++;
                continue;
            }

            this.imgTerrains[imgName] = new Image();
            this.imgTerrains[imgName].onload = function() {
                // console.log('Cached ' + this.src);
                loaded++;
                if (loaded == toLoad) {
                    // console.log('Loaded ' + loaded + ' terrain assets');
                    if (callbackFunction) {
                        callbackFunction();
                    }
                }
            }
            this.imgTerrains[imgName].src = '/static/smarthexboard/img/terrains/' + imgName;

        } else if (imgName.startsWith('feature_')) {
            if (typeof this.imgFeatures[imgName] !== "undefined") {
                loaded++;
                continue;
            }

            this.imgFeatures[imgName] = new Image();
            this.imgFeatures[imgName].onload = function() {
                // console.log('Cached ' + this.src);
                loaded++;
                if (loaded == toLoad) {
                    // console.log('Loaded ' + loaded + ' terrain assets');
                    if (callbackFunction) {
                        callbackFunction();
                    }
                }
            }
            this.imgFeatures[imgName].src = '/static/smarthexboard/img/features/' + imgName;

        } else if (imgName.startsWith('resource_')) {
            if (typeof this.imgResources[imgName] !== "undefined") {
                loaded++;
                continue;
            }

            this.imgResources[imgName] = new Image();
            this.imgResources[imgName].onload = function() {
                // console.log('Cached ' + this.src);
                loaded++;
                if (loaded == toLoad) {
                    // console.log('Loaded ' + loaded + ' terrain assets');
                    if (callbackFunction) {
                        callbackFunction();
                    }
                }
            }
            this.imgResources[imgName].src = '/static/smarthexboard/img/resources/' + imgName;
        } else {
            throw new Error('image type not handled: ' + imgName);
        }
    }
}

// Cleans up unused unit images
Renderer.prototype.cleanupTerrainImagesCache = function(imgList) {
    for (var i in imgTerrains) {
        if (typeof imgList[imgUnits[i]] !== "undefined") {
            // console.log("Removing unused entry %s", imgUnits[i].src);
            imgTerrains[i] = null;
            delete(imgTerrains[i]);
        }
    }
}

export { Renderer };