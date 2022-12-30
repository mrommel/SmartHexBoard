/**
 * Map - Provides map, player and hex objects
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

// TerrainType Constructor

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

// FeatureType Constructor

function FeatureType(name, texture) {
    this.name = name;
    this.texture = texture;
}

FeatureType.prototype.clone = function() {
    return new FeatureType(this.name, this.texture);
}

FeatureType.prototype.toString = function() {
    return '[FeatureType: ' + this.name + ']';
}

const FeatureTypes = {
    none: new FeatureType("none", "feature_none@3x.png"),
	// ...
}

// ResourceType Constructor

function ResourceType(name, texture) {
    this.name = name;
    this.texture = texture;
}

ResourceType.prototype.clone = function() {
    return new ResourceType(this.name, this.texture);
}

ResourceType.prototype.toString = function() {
    return '[ResourceType: ' + this.name + ']';
}

const ResourceTypes = {
    none: new ResourceType("none", "resource_none@3x.png"),
	aluminium: new ResourceType("aluminium", "resource_aluminium@3x.png"),
	antiquitySite: new ResourceType("antiquitySite", "resource_antiquitySite@3x.png"),
	fish: new ResourceType("fish", "resource_fish@3x.png"),
	oil: new ResourceType("oil", "resource_oil@3x.png"),
	sheep: new ResourceType("sheep", "resource_sheep@3x.png"),
	whales: new ResourceType("whales", "resource_whales@3x.png"),
	wheat: new ResourceType("wheat", "resource_wheat@3x.png"),
}

// Tile Constructor

/**
 * constructor of a Tile - a unique point on the map
 *
 * @param {TerrainType} terrainType terrain of tile
 * @param {FeatureType} featureType feature of tile
 * @param {ResourceType} resourceType resource of tile
 */
function Tile(terrainType, featureType, resourceType) {
    // handle terrain type
    if (!(terrainType instanceof TerrainType)) {
        throw new Error('expected type of first parameter is: TerrainType');
    } else {
        this.terrainType = terrainType;
    }

    // handle feature type
    if (typeof (featureType) == 'undefined') {
        this.featureType = FeatureTypes.none;
    } else if (!(featureType instanceof FeatureType)) {
        throw new Error('expected type of second parameter is: FeatureType');
    } else {
        this.featureType = featureType;
    }

    // handle resource type
    if (typeof (resourceType) == 'undefined') {
        this.resourceType = ResourceTypes.none;
    } else if (!(resourceType instanceof ResourceType)) {
        throw new Error('expected type of third parameter is: ResourceType');
    } else {
        this.resourceType = resourceType;
    }
}

Tile.prototype.toString = function() {
    return '[Tile: terrain=' + this.terrainType + ', feature=' + this.featureType + ', resource=' + this.resourceType + ']';
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

	for (var i = 0; i < this.cols; i++) {
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

Map.prototype.resourceAt = function(hexPoint) {
    return this.tiles[hexPoint.x][hexPoint.y].resourceType;
}

Map.prototype.modifyResourceAt = function(resourceType, hexPoint) {
    this.tiles[hexPoint.x][hexPoint.y].resourceType = resourceType;
}

Map.prototype.toString = function() {
    return '[Map: ' + this.cols + 'x' + this.rows + ']';
}