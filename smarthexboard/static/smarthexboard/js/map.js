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

function FeatureType(name, textures) {
    this.name = name;
    this.textures = textures;
}

FeatureType.prototype.clone = function() {
    return new FeatureType(this.name, this.textures);
}

FeatureType.prototype.toString = function() {
    return '[FeatureType: ' + this.name + ']';
}

const FeatureTypes = {
    none: new FeatureType("none", ["feature_none@3x.png"]),
    atoll: new FeatureType("atoll", ["feature_atoll@3x.png"]),
    fallout: new FeatureType("fallout", ["feature_fallout@3x.png"]),
    floodplains: new FeatureType("floodplains", ["feature_floodplains@3x.png"]),
    forest: new FeatureType("forest", ["feature_forest1@3x.png", "feature_forest2@3x.png"]),
    ice: new FeatureType("ice", ["feature_ice1@3x.png", "feature_ice2@3x.png", "feature_ice3@3x.png", "feature_ice4@3x.png", "feature_ice5@3x.png", "feature_ice6@3x.png"]),
	marsh: new FeatureType("marsh", ["feature_marsh1@3x.png", "feature_marsh2@3x.png"]),
	mountains: new FeatureType("mountains", ["feature_mountains1@3x.png", "feature_mountains2@3x.png", "feature_mountains3@3x.png"]),
	oasis: new FeatureType("oasis", ["feature_oasis@3x.png"]),
	// special case for pine forest
	pine: new FeatureType("pine", ["feature_pine1@3x.png", "feature_pine2@3x.png"]),
	rainforest: new FeatureType("rainforest", ["feature_rainforest1@3x.png", "feature_rainforest2@3x.png"]),
	reef: new FeatureType("reef", ["feature_reef1@3x.png", "feature_reef2@3x.png", "feature_reef3@3x.png"]),
}

// ResourceType Constructor

function ResourceType(name, texture) {
    this.name = name;
    this.texture = texture;
}

ResourceType.prototype.clone = function() {
    return new ResourceType(this.name, this.textures);
}

ResourceType.prototype.toString = function() {
    return '[ResourceType: ' + this.name + ']';
}

const ResourceTypes = {
    none: new ResourceType("none", "resource_none@3x.png"),
	aluminium: new ResourceType("aluminium", "resource_aluminium@3x.png"),
	antiquitySite: new ResourceType("antiquitySite", "resource_antiquitySite@3x.png"),
	banana: new ResourceType("banana", "resource_banana@3x.png"),
	cattle: new ResourceType("cattle", "resource_cattle@3x.png"),
	citrus: new ResourceType("citrus", "resource_citrus@3x.png"),
	coal: new ResourceType("coal", "resource_coal@3x.png"),
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

/**
 * check if hexPoint is on the map
 *
 * @param {HexPoint} hexPoint point to be checked
 * @return true if point is on the map
 */
Map.prototype.valid = function(hexPoint) {
    return 0 <= hexPoint.x && hexPoint.x < this.cols && 0 <= hexPoint.y && hexPoint.y < this.rows;
}

Map.prototype.tileAt = function(hexPoint) {
    // check point is on map
    if (!this.valid(hexPoint)) {
        throw new Error(hexPoint + ' is not on the map');
    }

    return this.tiles[hexPoint.x][hexPoint.y];
}

Map.prototype.terrainAt = function(hexPoint) {
    // check point is on map
    if (!this.valid(hexPoint)) {
        throw new Error(hexPoint + ' is not on the map');
    }

    return this.tiles[hexPoint.x][hexPoint.y].terrainType;
}

Map.prototype.modifyTerrainAt = function(terrainType, hexPoint) {
    // check point is on map
    if (!this.valid(hexPoint)) {
        throw new Error(hexPoint + ' is not on the map');
    }

    // check terrainType is of correct type
    if (!(terrainType instanceof TerrainType)) {
        throw new Error(terrainType + ' is not of type TerrainType');
    }

    this.tiles[hexPoint.x][hexPoint.y].terrainType = terrainType;
}

Map.prototype.featureAt = function(hexPoint) {
    // check point is on map
    if (!this.valid(hexPoint)) {
        throw new Error(hexPoint + ' is not on the map');
    }

    return this.tiles[hexPoint.x][hexPoint.y].featureType;
}

Map.prototype.modifyFeatureAt = function(featureType, hexPoint) {
    // check point is on map
    if (!this.valid(hexPoint)) {
        throw new Error(hexPoint + ' is not on the map');
    }

    // check featureType is of correct type
    if (!(featureType instanceof FeatureType)) {
        throw new Error(featureType + ' is not of type FeatureType');
    }

    this.tiles[hexPoint.x][hexPoint.y].featureType = featureType;
}

Map.prototype.resourceAt = function(hexPoint) {
    // check point is on map
    if (!this.valid(hexPoint)) {
        throw new Error(hexPoint + ' is not on the map');
    }

    return this.tiles[hexPoint.x][hexPoint.y].resourceType;
}

Map.prototype.modifyResourceAt = function(resourceType, hexPoint) {
    // check point is on map
    if (!this.valid(hexPoint)) {
        throw new Error(hexPoint + ' is not on the map');
    }

    // check resourceType is of correct type
    if (!(resourceType instanceof ResourceType)) {
        throw new Error(resourceType + ' is not of type ResourceType');
    }

    this.tiles[hexPoint.x][hexPoint.y].resourceType = resourceType;
}

Map.prototype.toString = function() {
    return '[Map: ' + this.cols + 'x' + this.rows + ']';
}