/**
 * Renderer - draws the graphic elements on canvases
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

import { CGPoint } from './base/prototypes.js';
import { HexPoint, HexDirections, HexDirection } from './base/point.js';
import { TerrainTypes, BeachTypes, SnowTypes, FeatureTypes, ResourceTypes } from './map/types.js';
import { TechTypes } from './game/types.js';
import { Map } from './map/map.js';
import { Assets } from './assets.js';

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

	// image cache
	this.assets = new Assets();

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

Renderer.prototype.cacheImages = function(callbackFunction) {

    var _this = this;
    this.assets.cacheTileImages(function() {
        _this.assets.cacheGameImages(function() {
            callbackFunction();
            console.log('tile and game assets cached');
        });
    });
}

Renderer.prototype.texturesLoaded = function() {

    return this.assets.tileTexturesLoaded && this.assets.gameTexturesLoaded;
}

Renderer.prototype.coastTextureNameAt = function(hexPoint) {
    if (!(hexPoint instanceof HexPoint)) {
        throw new Error(hexPoint + ' is not a HexPoint');
    }

    const terrain = this.map.terrainAt(hexPoint);

    if (!terrain.isWater()) {
        return null;
    }

    var textureName = "beach"; // "beach-n-ne-se-s-sw-nw"
    var _this = this; // context this is not visible on forEach loop
    // console.log(Object.values(HexDirections));
    Object.values(HexDirections).forEach(function(direction) {
        const neighborPoint = hexPoint.neighborIn(direction, 1);

        if (!_this.map.valid(neighborPoint)) {
            return;
        }

        var neighborTerrain = _this.map.terrainAt(neighborPoint);
        if (!neighborTerrain.isWater()) {
            textureName = textureName + "-" + direction.short();
        }
    });

    // console.log('coastTextureNameAt(' + hexPoint + ') => ' + textureName);

    if (textureName == "beach") {
        return null;
    }

    return textureName + '@3x.png';
}

Renderer.prototype.terrainImageAt = function(hexPoint) {
    if (!(hexPoint instanceof HexPoint)) {
        throw new Error(hexPoint + ' is not a HexPoint');
    }

    //
    var textureName = "";
    const coastTexture = this.coastTextureNameAt(hexPoint);
    if (coastTexture != null) {
        textureName = coastTexture;
    } else {
        var terrain = this.map.terrainAt(hexPoint);
        var textureNames = [];

        if (this.map.isHillsAt(hexPoint)) {
            textureNames = terrain.hillsTextures;
        } else {
            textureNames = terrain.textures;
        }

        var index = Math.abs(hexPoint.x + hexPoint.y) % textureNames.length;
        textureName = textureNames[index];
    }

    return this.assets.terrainTexture(textureName);
}

Renderer.prototype.snowImageAt = function(hexPoint) {
    if (!(hexPoint instanceof HexPoint)) {
        throw new Error(hexPoint + ' is not a HexPoint');
    }

    var textureName = "snow"; // "snow-n-ne-se-s-sw-nw"

    const terrain = this.map.terrainAt(hexPoint);
    if (terrain.isWater()) {
        textureName = "snow-to-water";
    }

    var _this = this; // context this is not visible on forEach loop
    Object.values(HexDirections).forEach(function(direction) {
        const neighborPoint = hexPoint.neighborIn(direction, 1);

        if (!_this.map.valid(neighborPoint)) {
            return;
        }

        const neighborTerrain = _this.map.terrainAt(neighborPoint);
        if (neighborTerrain == TerrainTypes.snow) {
            textureName = textureName + ("-" + direction.short());
        }
    });

    if (textureName == "snow" || textureName == "snow-to-water") {
        return null;
    }

    return this.assets.terrainTexture(textureName);
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

    this.featuresCanvas = document.getElementById('features');
    this.featuresCtx = this.featuresCanvas.getContext('2d');
    this.featuresCtx.clearRect(spos.x, spos.y, epos.x - spos.x, epos.y - spos.y);

    this.resourcesCanvas = document.getElementById('resources');
    this.resourcesCtx = this.resourcesCanvas.getContext('2d');
    this.resourcesCtx.clearRect(spos.x, spos.y, epos.x - spos.x, epos.y - spos.y);

    // debug - fill complete canvas
    var canvasSize = this.map.canvasSize();
    var canvasOffset = this.map.canvasOffset();
    this.terrainsCtx.beginPath();
    this.terrainsCtx.rect(0, 0, canvasSize.width, canvasSize.height);
    this.terrainsCtx.fillStyle = "black";
    this.terrainsCtx.fill();

    // console.log('render x=' + renderZone.srow + ' - ' + renderZone.erow);
    for (var row = renderZone.srow; row < renderZone.erow; row++) {
        // we space the hexagons on each line next column being on the row below
        for (var col = renderZone.scol; col < renderZone.ecol; col++) {

            // hex = map.map[row][col];
            var hex = new HexPoint(col, row);
            // console.log('hex=' + hex);
            var screen = hex.toScreen();
            // console.log('canvasSize.height=' + canvasSize.height + ', screen.y=' + (screen.y + canvasOffset.y));
            screen.y = canvasSize.height - (screen.y + canvasOffset.y) - canvasOffset.y;
            // console.log('screen=' + screen);

            var terrainImage = this.terrainImageAt(hex);
            this.terrainsCtx.drawImage(terrainImage, screen.x + canvasOffset.x, screen.y + canvasOffset.y, 72, 72);

            var snowImage = this.snowImageAt(hex);
            if (snowImage != null) {
                this.terrainsCtx.drawImage(snowImage, screen.x + canvasOffset.x, screen.y + canvasOffset.y, 72, 72);
            }
            // console.log('render tile at: ' + col + ', ' + row + ' => ' + x0 + ', ' + y0);

            var feature = this.map.featureAt(hex);
            if (feature.name != FeatureTypes.none.name) {
                // console.log('feature=' + feature + ', at=' + hex);
                var index = Math.abs(hex.x + hex.y) % feature.textures.length;
                var textureName = feature.textures[index];
                var img = this.assets.featureTexture(textureName);
                this.resourcesCtx.drawImage(img, screen.x + canvasOffset.x, screen.y + canvasOffset.y, 72, 72);
            }

            var resource = this.map.resourceAt(hex);
            if (resource.name != ResourceTypes.none.name) {
                // console.log('resource=' + resource + ', at=' + hex + ', tex=' + resource.texture);
                var img = this.assets.resourceTexture(resource.texture);
                this.resourcesCtx.drawImage(img, screen.x + canvasOffset.x, screen.y + canvasOffset.y, 72, 72);
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

export { Renderer };