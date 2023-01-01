/**
 * Map - Provides map, player and hex objects
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

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

export { FeatureType, FeatureTypes };