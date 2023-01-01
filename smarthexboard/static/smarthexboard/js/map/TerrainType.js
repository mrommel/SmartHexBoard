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

export { TerrainType, TerrainTypes };