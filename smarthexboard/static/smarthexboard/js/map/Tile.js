/**
 * Map - Provides map, player and hex objects
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

import { TerrainType } from './TerrainType.js';
import { FeatureType, FeatureTypes } from './FeatureType.js';
import { ResourceType, ResourceTypes } from './ResourceType.js';

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

export { Tile };