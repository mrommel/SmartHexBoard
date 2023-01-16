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

function TerrainType(name, textures, hillsTextures) {
    this.name = name;
    this.textures = textures;
    this.hillsTextures = hillsTextures;
}

TerrainType.prototype.clone = function() {
    return new TerrainType(this.name, this.texture);
}

TerrainType.prototype.isWater = function() {
    return this.name == GenerationTypes.water.name || this.name == TerrainTypes.ocean.name || this.name == TerrainTypes.shore.name;
}

TerrainType.prototype.isLand = function() {
    return this.name != GenerationTypes.water.name && this.name != TerrainTypes.ocean.name && this.name != TerrainTypes.shore.name;
}

TerrainType.prototype.toString = function() {
    return '[TerrainType: ' + this.name + ']';
}

const TerrainTypes = {
	desert: new TerrainType("desert", ["terrain_desert@3x.png"], ["terrain_desert_hills@3x.png", "terrain_desert_hills2@3x.png", "terrain_desert_hills3@3x.png"]),
	grass: new TerrainType("grass", ["terrain_grass@3x.png"], ["terrain_grass_hills@3x.png", "terrain_grass_hills2@3x.png", "terrain_grass_hills3@3x.png"]),
	ocean: new TerrainType("ocean", ["terrain_ocean@3x.png"], []),
	plains: new TerrainType("plains", ["terrain_plains@3x.png"], ["terrain_plains_hills@3x.png", "terrain_plains_hills2@3x.png", "terrain_plains_hills3@3x.png"]),
	shore: new TerrainType("shore", ["terrain_shore@3x.png"], []),
	snow: new TerrainType("snow", ["terrain_snow@3x.png"], ["terrain_snow_hills@3x.png", "terrain_snow_hills2@3x.png", "terrain_snow_hills3@3x.png"]),
	tundra: new TerrainType("tundra", ["terrain_tundra@3x.png", "terrain_tundra2@3x.png", "terrain_tundra3@3x.png"], ["terrain_tundra_hills@3x.png"]),
}

// map generation
const GenerationTypes = {
    water: new TerrainType("water", ["water@3x.png"], []),
	land: new TerrainType("land", ["land@3x.png"], []),
}

const BeachTypes = {
    beach_n_ne_nw: new TerrainType("beach-n-ne-nw", ["beach-n-ne-nw@3x.png"]),
    beach_n_ne_s_nw: new TerrainType("beach-n-ne-s-nw", ["beach-n-ne-s-nw@3x.png"]),
    beach_n_ne_s_sw_nw: new TerrainType("beach-n-ne-s-sw-nw", ["beach-n-ne-s-sw-nw@3x.png"]),
    beach_n_ne_s_sw: new TerrainType("beach-n-ne-s-sw", ["beach-n-ne-s-sw@3x.png"]),
    beach_n_ne_s: new TerrainType("beach-n-ne-s", ["beach-n-ne-s@3x.png"]),
    beach_n_ne_se_nw: new TerrainType("beach-n-ne-se-nw", ["beach-n-ne-se-nw@3x.png"]),
    beach_n_ne_se_s_nw: new TerrainType("beach-n-ne-se-s-nw", ["beach-n-ne-se-s-nw@3x.png"]),
    beach_n_ne_se_s_sw_nw: new TerrainType("beach-n-ne-se-s-sw-nw", ["beach-n-ne-se-s-sw-nw@3x.png"]),
    beach_n_ne_se_s_sw: new TerrainType("beach-n-ne-se-s-sw", ["beach-n-ne-se-s-sw@3x.png"]),
    beach_n_ne_se_s: new TerrainType("beach-n-ne-se-s", ["beach-n-ne-se-s@3x.png"]),
    beach_n_ne_se_sw_nw: new TerrainType("beach-n-ne-se-sw-nw", ["beach-n-ne-se-sw-nw@3x.png"]),
    beach_n_ne_se_sw: new TerrainType("beach-n-ne-se-sw", ["beach-n-ne-se-sw@3x.png"]),
    beach_n_ne_se: new TerrainType("beach-n-ne-se", ["beach-n-ne-se@3x.png"]),
    beach_n_ne_sw_nw: new TerrainType("beach-n-ne-sw-nw", ["beach-n-ne-sw-nw@3x.png"]),
    beach_n_ne_sw: new TerrainType("beach-n-ne-sw", ["beach-n-ne-sw@3x.png"]),
    beach_n_ne: new TerrainType("beach-n-ne", ["beach-n-ne@3x.png"]),
    beach_n_nw: new TerrainType("beach-n-nw", ["beach-n-nw@3x.png"]),
    beach_n_s_nw: new TerrainType("beach-n-s-nw", ["beach-n-s-nw@3x.png"]),
    beach_n_s_sw_nw: new TerrainType("beach-n-s-sw-nw", ["beach-n-s-sw-nw@3x.png"]),
    beach_n_s_sw: new TerrainType("beach-n-s-sw", ["beach-n-s-sw@3x.png"]),
    beach_n_s: new TerrainType("beach-n-s", ["beach-n-s@3x.png"]),
    beach_n_se_nw: new TerrainType("beach-n-se-nw", ["beach-n-se-nw@3x.png"]),
    beach_n_se_s_nw: new TerrainType("beach-n-se-s-nw", ["beach-n-se-s-nw@3x.png"]),
    beach_n_se_s_sw_nw: new TerrainType("beach-n-se-s-sw-nw", ["beach-n-se-s-sw-nw@3x.png"]),
    beach_n_se_s_sw: new TerrainType("beach-n-se-s-sw", ["beach-n-se-s-sw@3x.png"]),
    beach_n_se_s: new TerrainType("beach-n-se-s", ["beach-n-se-s@3x.png"]),
    beach_n_se_sw_nw: new TerrainType("beach-n-se-sw-nw", ["beach-n-se-sw-nw@3x.png"]),
    beach_n_se_sw: new TerrainType("beach-n-se-sw", ["beach-n-se-sw@3x.png"]),
    beach_n_se: new TerrainType("beach-n-se", ["beach-n-se@3x.png"]),
    beach_n_sw_nw: new TerrainType("beach-n-sw-nw", ["beach-n-sw-nw@3x.png"]),
    beach_n_sw: new TerrainType("beach-n-sw", ["beach-n-sw@3x.png"]),
    beach_n: new TerrainType("beach-n", ["beach-n@3x.png"]),
    beach_ne_nw: new TerrainType("beach-ne-nw", ["beach-ne-nw@3x.png"]),
    beach_ne_s_nw: new TerrainType("beach-ne-s-nw", ["beach-ne-s-nw@3x.png"]),
    beach_ne_s_sw_nw: new TerrainType("beach-ne-s-sw-nw", ["beach-ne-s-sw-nw@3x.png"]),
    beach_ne_s_sw: new TerrainType("beach-ne-s-sw", ["beach-ne-s-sw@3x.png"]),
    beach_ne_s: new TerrainType("beach-ne-s", ["beach-ne-s@3x.png"]),
    beach_ne_se_nw: new TerrainType("beach-ne-se-nw", ["beach-ne-se-nw@3x.png"]),
    beach_ne_se_s_nw: new TerrainType("beach-ne-se-s-nw", ["beach-ne-se-s-nw@3x.png"]),
    beach_ne_se_s_sw_nw: new TerrainType("beach-ne-se-s-sw-nw", ["beach-ne-se-s-sw-nw@3x.png"]),
    beach_ne_se_s_sw: new TerrainType("beach-ne-se-s-sw", ["beach-ne-se-s-sw@3x.png"]),
    beach_ne_se_s: new TerrainType("beach-ne-se-s", ["beach-ne-se-s@3x.png"]),
    beach_ne_se_sw_nw: new TerrainType("beach-ne-se-sw-nw", ["beach-ne-se-sw-nw@3x.png"]),
    beach_ne_se_sw: new TerrainType("beach-ne-se-sw", ["beach-ne-se-sw@3x.png"]),
    beach_ne_se: new TerrainType("beach-ne-se", ["beach-ne-se@3x.png"]),
    beach_ne_sw_nw: new TerrainType("beach-ne-sw-nw", ["beach-ne-sw-nw@3x.png"]),
    beach_ne_sw: new TerrainType("beach-ne-sw", ["beach-ne-sw@3x.png"]),
    beach_ne: new TerrainType("beach-ne", ["beach-ne@3x.png"]),
    beach_nw: new TerrainType("beach-nw", ["beach-nw@3x.png"]),
    beach_s_nw: new TerrainType("beach-s-nw", ["beach-s-nw@3x.png"]),
    beach_s_sw_nw: new TerrainType("beach-s-sw-nw", ["beach-s-sw-nw@3x.png"]),
    beach_s_sw: new TerrainType("beach-s-sw", ["beach-s-sw@3x.png"]),
    beach_s: new TerrainType("beach-s", ["beach-s@3x.png"]),
    beach_se_nw: new TerrainType("beach-se-nw", ["beach-se-nw@3x.png"]),
    beach_se_s_nw: new TerrainType("beach-se-s-nw", ["beach-se-s-nw@3x.png"]),
    beach_se_s_sw_nw: new TerrainType("beach-se-s-sw-nw", ["beach-se-s-sw-nw@3x.png"]),
    beach_se_s_sw: new TerrainType("beach-se-s-sw", ["beach-se-s-sw@3x.png"]),
    beach_se_s: new TerrainType("beach-se-s", ["beach-se-s@3x.png"]),
    beach_se_sw_nw: new TerrainType("beach-se-sw-nw", ["beach-se-sw-nw@3x.png"]),
    beach_se_sw: new TerrainType("beach-se-sw", ["beach-se-sw@3x.png"]),
    beach_se: new TerrainType("beach-se", ["beach-se@3x.png"]),
    beach_sw_nw: new TerrainType("beach-sw-nw", ["beach-sw-nw@3x.png"]),
    beach_sw: new TerrainType("beach-sw", ["beach-sw@3x.png"]),
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

// ClimateZones

// ResourceType Constructor

function ClimateZone(name) {
    this.name = name;
}

ClimateZone.prototype.toString = function() {
    return '[ClimateZone: ' + this.name + ']';
}

const ClimateZones = {
	polar: new ClimateZone("polar"),
	sub_polar: new ClimateZone("sub-polar"),
	temperate: new ClimateZone("temperate"),
	sub_tropic: new ClimateZone("sub-tropic"),
	tropic: new ClimateZone("tropic"),
}

export {
    TerrainType,
    TerrainTypes,
    GenerationTypes,
    BeachTypes,
    FeatureType,
    FeatureTypes,
    ResourceType,
    ResourceTypes,
    MapSize,
    MapSizes,
    ClimateZone,
    ClimateZones,
};