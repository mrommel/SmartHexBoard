/**
 * Map - Provides map, player and hex objects
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

function TerrainType(name, texture) {
    this.name = name;
    this.texture = texture;
}

TerrainType.prototype.clone = function() {
    return new TerrainType(this.name, this.texture);
}

TerrainType.prototype.toString = function() {
  return '[TerrainType: ' + this.name + ']';
}

const TerrainTypes = {
	desert: new TerrainType("desert", "terrain_desert@3x.png"),
	grass: new TerrainType("grass", "terrain_grass@3x.png"),
	ocean: new TerrainType("ocean", "terrain_ocean@3x.png"),
	plain: new TerrainType("plain", "terrain_plain@3x.png"),
	shore: new TerrainType("shore", "terrain_shore@3x.png"),
	snow: new TerrainType("snow", "terrain_snow@3x.png"),
	tundra: new TerrainType("tundra", "terrain_tundra@3x.png"),
}

// Tile Constructor

function Tile(terrainType) {
    this.terrainType = terrainType;
}

Tile.prototype.toString = function() {
  return '[Tile: ' + this.terrainType + ']';
}

// Map Constructor

function Map(cols, rows) {
    if (typeof (cols) == 'undefined' && typeof (rows) == 'undefined') {
        this.cols = 10;
	    this.rows = 10;
    } else {
	    this.cols = cols;
	    this.rows = rows;
	}

	this.tiles = Array(this.cols).fill().map(()=>Array(this.rows).fill());

	for (var i=0;i<this.cols;i++) {
        for (var j = 0; j < this.rows; j++) {
            this.tiles[i][j] = new Tile(TerrainTypes.ocean.clone());
        }
    }
}

// Map Object Public Methods

Map.prototype.copy = function(map) {
    this.rows = map.rows;
	this.cols = map.cols;

	this.tiles = map.tiles.map(function(arr) {
        return arr.slice();
    });
}

Map.prototype.tileAt = function(hexPoint) {
    return this.tiles[hexPoint.x][hexPoint.y];
}

Map.prototype.terrainAt = function(hexPoint) {
    // console.log(this);
    // console.log('terrainAt(' + hexPoint + ') = ' + this.tiles[hexPoint.x][hexPoint.y]);
    return this.tiles[hexPoint.x][hexPoint.y].terrainType;
}

Map.prototype.modifyTerrainAt = function(terrainType, hexPoint) {
    this.tiles[hexPoint.x][hexPoint.y].terrainType = terrainType;
}

Map.prototype.toString = function() {
    return '[Map: ' + this.cols + 'x' + this.rows + ']';
}