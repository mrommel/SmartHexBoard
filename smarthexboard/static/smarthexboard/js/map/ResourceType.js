/**
 * Map - Provides map, player and hex objects
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

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

export { ResourceType, ResourceTypes };