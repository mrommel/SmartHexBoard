/**
 * Map - Provides map, player and hex objects
 *
 * Copyright (c) 2023 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

import { TerrainType, FeatureType, FeatureTypes, ResourceType, ResourceTypes, ClimateZones } from './types.js';

// Tile Constructor

/**
 * constructor of a Tile - a unique point on the map
 *
 * @param {TerrainType} terrainType terrain of tile
 * @param {FeatureType} featureType feature of tile
 * @param {ResourceType} resourceType resource of tile
 */
function Tile(terrainType, featureType, resourceType) {
    // handle a terrain type
    if (!(terrainType instanceof TerrainType)) {
        throw new Error('expected type of first parameter is: TerrainType');
    } else {
        this.terrainType = terrainType;
    }

    // handle a feature type
    if (typeof (featureType) == 'undefined') {
        this.featureType = FeatureTypes.none;
    } else if (!(featureType instanceof FeatureType)) {
        throw new Error('expected type of second parameter is: FeatureType');
    } else {
        this.featureType = featureType;
    }

    // handle a resource type
    if (typeof (resourceType) == 'undefined') {
        this.resourceType = ResourceTypes.none;
    } else if (!(resourceType instanceof ResourceType)) {
        throw new Error('expected type of third parameter is: ResourceType');
    } else {
        this.resourceType = resourceType;
    }

    this.isHills = false;
    this.climateZone = ClimateZones.temperate;
}

Tile.prototype.toString = function() {
    return '[Tile: terrain=' + this.terrainType + ', hills=' + this.isHills + ', feature=' + this.featureType + ', resource=' + this.resourceType + ']';
}

export { Tile };