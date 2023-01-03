/**
 * Map - Provides map, player and hex objects
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

// MapSize Constructor

function MapSize(name, cols, rows) {
    this.name = name;
    this.cols = cols;
    this.rows = rows
}

MapSize.prototype.clone = function() {
    return new MapSize(this.name, this.cols, this.rows);
}

MapSize.prototype.toString = function() {
    return '[MapSize: ' + this.name + ' (' + this.cols + ', ' + this.rows + ')]';
}

const MapSizes = {
	duel: new MapSize("duel", 32, 22),
	// fogTilesPerBarbarianCamp: 13, maxActiveReligions: 2, targetNumberOfCities: 8,
    // numberOfPlayers: 2, numberOfNaturalWonders: 2, numberOfCityStates: 3
	tiny: new MapSize("tiny", 42, 32),
	// fogTilesPerBarbarianCamp: 18, maxActiveReligions: 4, targetNumberOfCities: 10,
    //numberOfPlayers: 3, numberOfNaturalWonders: 3, numberOfCityStates: 6
	small: new MapSize("small", 52, 42),
	// fogTilesPerBarbarianCamp: 23, maxActiveReligions: 5, targetNumberOfCities: 15,
    // numberOfPlayers: 4, numberOfNaturalWonders: 4, numberOfCityStates: 9
	standard: new MapSize("standard", 62, 52),
	// fogTilesPerBarbarianCamp: 27, maxActiveReligions: 7, targetNumberOfCities: 20,
    // numberOfPlayers: 6, numberOfNaturalWonders: 5, numberOfCityStates: 12
	large: new MapSize("large", 72, 62),
	// fogTilesPerBarbarianCamp: 30, maxActiveReligions: 9, targetNumberOfCities: 30,
    // numberOfPlayers: 8, numberOfNaturalWonders: 6, numberOfCityStates: 15
	huge: new MapSize("huge", 82, 72),
	/* fogTilesPerBarbarianCamp: 35, maxActiveReligions: 11, targetNumberOfCities: 45,
    numberOfPlayers: 10, numberOfNaturalWonders: 7, numberOfCityStates: 18*/
}

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

export { TerrainType, TerrainTypes, FeatureType, FeatureTypes, ResourceType, ResourceTypes, MapSize, MapSizes };