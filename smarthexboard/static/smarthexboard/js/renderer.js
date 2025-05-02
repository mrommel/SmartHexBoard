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

// image cache
const assets = new Assets();

// parent canvas renderer class
class CanvasRenderer {
    constructor(name) {
        this.name = name;
    }

    setup() {
        console.log('CanvasRenderer.setup() - should not happen');
    }

    clearRect(x, y, width, height) {
        console.log('CanvasRenderer.clearRect(...) - should not happen');
    }
}

// inheriting parent class
class TerrainCanvasRenderer extends CanvasRenderer {
    constructor() {
        super('TerrainCanvasRenderer.constructor()');

        this.terrainsCanvas = null;
	    this.terrainsCtx = null;
    }

    setup(map) {
        console.log('TerrainCanvasRenderer.setup()');

        this.map = map;

        // Check if the canvases already exists in the current document to prevent
        // overlaying multiple rendering instances
        if ((this.terrainsCanvas = document.getElementById('terrains')) === null) {
            this.terrainsCanvas = addTag('game', 'canvas');
        }
        this.terrainsCanvas.id = "terrains";
        this.terrainsCanvas.style.cssText = 'z-index: 0; position: absolute; left: 0px; top: 0px;';

        this.terrainsCtx = this.terrainsCanvas.getContext('2d');
        console.log('TerrainCanvasRenderer canvas created');
    }

    clearRect(x, y, width, height) {
        this.terrainsCtx.clearRect(x, y, width, height);
    }

    drawTile(hexPoint, x, y) {
        if (!(hexPoint instanceof HexPoint)) {
            throw new Error(hexPoint + ' is not a HexPoint');
        }

        // this.terrainsCtx.beginPath();
        // this.terrainsCtx.rect(0, 0, canvasSize.width, canvasSize.height);
        // this.terrainsCtx.rect(x, y, 72, 72);
        // this.terrainsCtx.fillStyle = "black";
        // this.terrainsCtx.fill();

        const terrainImage = this.terrainImageAt(hexPoint);
        this.terrainsCtx.drawImage(terrainImage, x, y, 72, 72);

        const snowImage = this.snowImageAt(hexPoint);
        if (snowImage != null) {
            this.terrainsCtx.drawImage(snowImage, x, y, 72, 72);
        }
        // console.log('render tile at: ' + col + ', ' + row + ' => ' + x0 + ', ' + y0);
    }

    coastTextureNameAt(hexPoint) {
        if (!(hexPoint instanceof HexPoint)) {
            throw new Error(hexPoint + ' is not a HexPoint');
        }

        const terrain = this.map.terrainAt(hexPoint);

        if (!terrain.isWater()) {
            return null;
        }

        let textureName = "beach"; // "beach-n-ne-se-s-sw-nw"
        const _this = this; // context this is not visible on forEach loop
        // console.log(Object.values(HexDirections));
        Object.values(HexDirections).forEach(function(direction) {
            const neighborPoint = hexPoint.neighborIn(direction, 1);

            if (!_this.map.valid(neighborPoint)) {
                return;
            }

            const neighborTerrain = _this.map.terrainAt(neighborPoint);
            if (!neighborTerrain.isWater()) {
                textureName = textureName + "-" + direction.short();
            }
        });

        // console.log('coastTextureNameAt(' + hexPoint + ') => ' + textureName);

        if (textureName === "beach") {
            return null;
        }

        return textureName + '@3x.png';
    }

    terrainImageAt(hexPoint) {
        if (!(hexPoint instanceof HexPoint)) {
            throw new Error(hexPoint + ' is not a HexPoint');
        }

        //
        let textureName = "";
        const coastTexture = this.coastTextureNameAt(hexPoint);
        if (coastTexture != null) {
            textureName = coastTexture;
        } else {
            const terrain = this.map.terrainAt(hexPoint);
            let textureNames = [];

            if (this.map.isHillsAt(hexPoint)) {
                textureNames = terrain.hillsTextures;
            } else {
                textureNames = terrain.textures;
            }

            const index = Math.abs(hexPoint.x + hexPoint.y) % textureNames.length;
            textureName = textureNames[index];
        }

        return assets.terrainTexture(textureName);
    }

    snowImageAt(hexPoint) {
        if (!(hexPoint instanceof HexPoint)) {
            throw new Error(hexPoint + ' is not a HexPoint');
        }

        let textureName = "snow"; // "snow-n-ne-se-s-sw-nw"

        const terrain = this.map.terrainAt(hexPoint);
        if (terrain.isWater()) {
            textureName = "snow-to-water";
        }

        const _this = this; // context this is not visible on forEach loop
        Object.values(HexDirections).forEach(function(direction) {
            const neighborPoint = hexPoint.neighborIn(direction, 1);

            if (!_this.map.valid(neighborPoint)) {
                return;
            }

            const neighborTerrain = _this.map.terrainAt(neighborPoint);
            if (neighborTerrain === TerrainTypes.snow) {
                textureName = textureName + ("-" + direction.short());
            }
        });

        if (textureName === "snow" || textureName === "snow-to-water") {
            return null;
        }

        return assets.terrainTexture(textureName);
    }
}

class FeatureCanvasRenderer extends CanvasRenderer {
    constructor() {
        super('FeatureCanvasRenderer.constructor()');

        this.featuresCanvas = null;
	    this.featuresCtx = null;
    }

    setup(map) {
        console.log('FeatureCanvasRenderer.setup()');

        this.map = map;

        // Check if the canvases already exists in the current document to prevent
        // overlaying multiple rendering instances
        if ((this.featuresCanvas = document.getElementById('features')) === null) {
            this.featuresCanvas = addTag('game', 'canvas');
        }
        this.featuresCanvas.id = "features";
        this.featuresCanvas.style.cssText = 'z-index: 3; position: absolute; left: 0px; top: 0px;';

        this.featuresCtx = this.featuresCanvas.getContext('2d');
        console.log('FeatureCanvasRenderer canvas created');
    }

    clearRect(x, y, width, height) {
        this.featuresCtx.clearRect(x, y, width, height);
    }

    drawTile(hexPoint, x, y) {
        if (!(hexPoint instanceof HexPoint)) {
            throw new Error(hexPoint + ' is not a HexPoint');
        }

        var feature = this.map.featureAt(hexPoint);
        if (feature.name !== FeatureTypes.none.name) {
            // console.log('feature=' + feature + ', at=' + hex);
            const index = Math.abs(hexPoint.x + hexPoint.y) % feature.textures.length;
            const textureName = feature.textures[index];
            const img = assets.featureTexture(textureName);
            this.featuresCtx.drawImage(img, x, y, 72, 72);
        }
    }
}

class ResourceCanvasRenderer extends CanvasRenderer {
    constructor() {
        super('ResourceCanvasRenderer.constructor()');

        this.resourcesCanvas = null;
	    this.resourcesCtx = null;
    }

    setup(map) {
        console.log('ResourceCanvasRenderer.setup()');

        this.map = map;

        if ((this.resourcesCanvas = document.getElementById('resources')) === null) {
            this.resourcesCanvas = addTag('game', 'canvas');
        }
        this.resourcesCanvas.id = "resources";
        this.resourcesCanvas.style.cssText = 'z-index: 2; position: absolute; left: 0px; top: 0px;';

        this.resourcesCtx = this.resourcesCanvas.getContext('2d');
        console.log('resources canvas created');
    }

    clearRect(x, y, width, height) {
        this.resourcesCtx.clearRect(x, y, width, height);
    }

    drawTile(hexPoint, x, y) {
        if (!(hexPoint instanceof HexPoint)) {
            throw new Error(hexPoint + ' is not a HexPoint');
        }

        const resource = this.map.resourceAt(hexPoint);
        if (resource.name !== ResourceTypes.none.name) {
            // console.log('resource=' + resource + ', at=' + hex + ', tex=' + resource.texture);
            const img = assets.resourceTexture(resource.texture);
            this.resourcesCtx.drawImage(img, x, y, 72, 72);
        }
    }
}

class CityCanvasRenderer extends CanvasRenderer {
    constructor() {
        super('CityCanvasRenderer.constructor()');

        this.citiesCanvas = null;
	    this.citiesCtx = null;
    }

    setup(map) {
        console.log('CityCanvasRenderer.setup()');

        this.map = map;

        if ((this.citiesCanvas = document.getElementById('cities')) === null) {
            this.citiesCanvas = addTag('game', 'canvas');
        }
        this.citiesCanvas.id = "cities";
        this.citiesCanvas.style.cssText = 'z-index: 4; position: absolute; left: 0px; top: 0px;';

        this.citiesCtx = this.citiesCanvas.getContext('2d');
        console.log('cities canvas created');
    }

    drawTile(hexPoint, x, y) {
        if (!(hexPoint instanceof HexPoint)) {
            throw new Error(hexPoint + ' is not a HexPoint');
        }

        const city = this.map.cityAt(hexPoint);
        if (city !== null) {
            console.log('city found: ' + city.toString());
            const img = assets.cityTexture(city);
            // console.log('draw unit ' + unit.unitType + ' at ' + unit.location);
            this.citiesCtx.drawImage(img, x, y, 72, 72);
        }
    }

    clearRect(x, y, width, height) {
        this.citiesCtx.clearRect(x, y, width, height);
    }
}

class UnitCanvasRenderer extends CanvasRenderer {
    constructor() {
        super('UnitCanvasRenderer.constructor()');

        this.unitsCanvas = null;
	    this.unitsCtx = null;
    }

    setup(map) {
        console.log('UnitCanvasRenderer.setup()');

        this.map = map;

        if ((this.unitsCanvas = document.getElementById('units')) === null) {
            this.unitsCanvas = addTag('game', 'canvas');
        }
        this.unitsCanvas.id = "units";
        this.unitsCanvas.style.cssText = 'z-index: 5; position: absolute; left: 0px; top: 0px;';

        this.unitsCtx = this.unitsCanvas.getContext('2d');
        console.log('units canvas created');
    }

    drawTile(hexPoint, x, y) {
        if (!(hexPoint instanceof HexPoint)) {
            throw new Error(hexPoint + ' is not a HexPoint');
        }

        const units = this.map.unitsAt(hexPoint);
        units.forEach((unit) => {
            const img = assets.unitTexture(unit.unitType.texture);
            // console.log('draw unit ' + unit.unitType + ' at ' + unit.location);
            this.unitsCtx.drawImage(img, x, y, 72, 72);
        });
    }

    clearRect(x, y, width, height) {
        this.unitsCtx.clearRect(x, y, width, height);
    }
}

class CursorCanvasRenderer extends CanvasRenderer {
    constructor() {
        super('CursorCanvasRenderer.constructor()');

        this.cursorCanvas = null;
	    this.cursorCtx = null;
    }

    setup(map) {
        console.log('CursorCanvasRenderer.setup()');

        this.map = map;

        if ((this.cursorCanvas = document.getElementById('cursor')) === null) {
            this.cursorCanvas = addTag('game', 'canvas');
        }
        this.cursorCanvas.id = "cursor";
        this.cursorCanvas.style.cssText = 'z-index: 1; position: absolute; left: 0px; top: 0px;';

        this.cursorCtx = this.cursorCanvas.getContext('2d');
        console.log('cursor canvas created');
    }

    drawTile(hexPoint, x, y) {
        if (!(hexPoint instanceof HexPoint)) {
            throw new Error(hexPoint + ' is not a HexPoint');
        }

        this.cursorCtx.drawImage(this.cursorImage, x, y + 24, 72, 48);
    }

    clearRect(x, y, width, height) {
        this.cursorCtx.clearRect(x, y, width, height);
    }
}

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

	// internal renderers
	this.terrainRenderer = new TerrainCanvasRenderer();
	this.featureRenderer = new FeatureCanvasRenderer();
	this.resourceRenderer = new ResourceCanvasRenderer();
    this.cityRenderer = new CityCanvasRenderer();
	this.unitRenderer = new UnitCanvasRenderer();
	this.cursorRenderer = new CursorCanvasRenderer();

    // canvasOffsetX = window.innerWidth/2 - imgMapBackground.width/2;
    if (this.canvasOffsetX < 0) { this.canvasOffsetX = 0; }

    // Set the width/height of the container div to browser window width/height
    // This improves the performance. User will scroll the div instead of window
    document.getElementById('game').style.width = window.innerWidth + "px";
    document.getElementById('game').style.height = window.innerHeight + "px";
    document.getElementById('game').tabIndex = 1; // For focusing the game area
    document.getElementById('game').focus();
}

Renderer.prototype.setup = function(map) {
    this.map = map;  // @fixme

    this.terrainRenderer.setup(map);
    this.featureRenderer.setup(map);
    this.resourceRenderer.setup(map);
    this.cityRenderer.setup(map);
    this.unitRenderer.setup(map);
    this.cursorRenderer.setup(map);
}

Renderer.prototype.cacheImages = function(callbackFunction) {

    assets.cacheTileImages(function() {
        assets.cacheGameImages(function() {
            callbackFunction();
            console.log('tile and game assets cached');
        });
    });
}

Renderer.prototype.texturesLoaded = function() {

    return assets.tileTexturesLoaded && assets.gameTexturesLoaded;
}

Renderer.prototype.render = function(orow, ocol, range) {

    // console.log('==> render tile at: ' + ocol + ', ' + orow);

    // the map (cell) coords that clearRect will clear
    const clearZone = this.getZoneRangeLimits(orow, ocol, range + 1);
    // the map (cell) coords that will be rendered hex by hex
    const renderZone = this.getZoneRangeLimits(orow, ocol, range + 2);

    const spos = this.cellToScreen(clearZone.srow, clearZone.scol, false);
    const epos = this.cellToScreen(clearZone.erow, clearZone.ecol, false);

    this.terrainRenderer.clearRect(spos.x, spos.y, epos.x - spos.x, epos.y - spos.y);
    this.featureRenderer.clearRect(spos.x, spos.y, epos.x - spos.x, epos.y - spos.y);
    this.resourceRenderer.clearRect(spos.x, spos.y, epos.x - spos.x, epos.y - spos.y);
    this.cityRenderer.clearRect(spos.x, spos.y, epos.x - spos.x, epos.y - spos.y);
    this.unitRenderer.clearRect(spos.x, spos.y, epos.x - spos.x, epos.y - spos.y);
    // this.cursorRenderer.clearRect(spos.x, spos.y, epos.x - spos.x, epos.y - spos.y);

    // debug - fill complete canvas
    const canvasSize = this.map.canvasSize();
    const canvasOffset = this.map.canvasOffset();

    // console.log('render x=' + renderZone.srow + ' - ' + renderZone.erow);
    for (let row = renderZone.srow; row < renderZone.erow; row++) {
        // we space the hexagons on each line next column being on the row below
        for (let col = renderZone.scol; col < renderZone.ecol; col++) {

            // hex = map.map[row][col];
            const hex = new HexPoint(col, row);
            // console.log('hex=' + hex);
            const screen = hex.toScreen();
            // console.log('canvasSize.height=' + canvasSize.height + ', screen.y=' + (screen.y + canvasOffset.y));
            screen.y = canvasSize.height - (screen.y + canvasOffset.y) - canvasOffset.y;
            // console.log('screen=' + screen);

            this.terrainRenderer.drawTile(hex, screen.x + canvasOffset.x, screen.y + canvasOffset.y);
            this.featureRenderer.drawTile(hex, screen.x + canvasOffset.x, screen.y + canvasOffset.y);
            this.resourceRenderer.drawTile(hex, screen.x + canvasOffset.x, screen.y + canvasOffset.y);
            this.cityRenderer.drawTile(hex, screen.x + canvasOffset.x, screen.y + canvasOffset.y);
            this.unitRenderer.drawTile(hex, screen.x + canvasOffset.x, screen.y + canvasOffset.y);
        }
    }
}

Renderer.prototype.renderCursor = function(hexPoint) {

    const canvasSize = this.map.canvasSize();
    const canvasOffset = this.map.canvasOffset();

    this.cursorRenderer.clearRect(0, 0, canvasSize.width, canvasSize.height);

    // draw cursor
    const screen = hexPoint.toScreen();
    screen.y = canvasSize.height - (screen.y + canvasOffset.y) - canvasOffset.y;

    if (this.cursorRenderer.cursorImage == null) {
        const cursorImage = new Image();
        const _this = this;
        cursorImage.onload = function() {
            _this.cursorRenderer.cursorImage = this;
            _this.cursorRenderer.drawTile(hexPoint, screen.x + canvasOffset.x, screen.y + canvasOffset.y/* + 24*/);
        }
        cursorImage.src = '/static/smarthexboard/img/ui/focus1@3x.png';
    } else {
        this.cursorRenderer.drawTile(hexPoint, screen.x + canvasOffset.x, screen.y + canvasOffset.y/* + 24*/);
    }

    // console.log('Draw cursor at ' + hexPoint);
}

Renderer.prototype.clearCursor = function() {

    const canvasSize = this.map.canvasSize();
    this.cursorRenderer.clearRect(0, 0, canvasSize.width, canvasSize.height);
}

// Returns min and max row,col for a range around a cell(row,col)
Renderer.prototype.getZoneRangeLimits =	function(row, col, range) {

    const z = {srow: 0, scol: 0, erow: this.map.rows, ecol: this.map.cols};

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

    let x0, y0;

    if (col & 1) { // odd column
        y0 =  row * 2 * this.r + this.r + this.renderOffsetY;
        x0 =  col * (this.s + this.h) + this.h + this.renderOffsetX;
    } else {
        y0 = row * 2 * this.r  + this.renderOffsetY;
        x0 = col * (this.s + this.h) + this.h + this.renderOffsetX;
    }

    if (absolute) {
        const vp = document.getElementById('game');
        x0 += this.canvasOffsetX - vp.clientLeft - vp.offsetLeft;
        y0 += this.canvasOffsetY - vp.clientTop - vp.offsetTop;
    }

    return new CGPoint(x0, y0);
}

// Converts from screen x,y to row,col in map array
Renderer.prototype.screenToCell = function(x, y) {

    let vrow; // virtual graphical rows
    let trow, tcol; // true map rows/cols

    tcol = Math.round((x - this.renderOffsetX) / this.colSlice + this.mousePrecisionOffset) - 1;
    // console.log(tcol);
    // a graphical row (half hex) not the array row
    vrow = (y - this.renderOffsetY * (~tcol & 1)) / this.r; // Half hexes add r if col is odd
    // shift to correct row index
    trow = Math.round(vrow/2 - (vrow & 1));
    if (trow < 0) { trow = 0; }
    if (trow > this.map.rows - 1) trow = this.map.rows - 1;
    if (tcol > this.map.cols - 1) tcol = this.map.cols - 1;
    return new Cell(trow, tcol);
}

export { Renderer };