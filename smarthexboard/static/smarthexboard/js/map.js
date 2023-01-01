/**
 * Map - Provides map, player and hex objects
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

import { TerrainType, TerrainTypes } from './map/TerrainType.js';
import { ResourceType } from './map/ResourceType.js';
import { FeatureType } from './map/FeatureType.js';
import { Tile } from './map/Tile.js';

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

export { Tile, Map };