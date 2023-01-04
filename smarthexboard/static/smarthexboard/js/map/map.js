/**
 * Map - Provides map, player and hex objects
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

import { TerrainType, TerrainTypes, FeatureType, ResourceType } from './types.js';
import { Tile } from './tile.js';

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

    this.units = []
    this.cities = []
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

/**
 * returns the tile at hexPoint
 *
 * @param {HexPoint} hexPoint point to return the tile for
 * @return {Tile} at hexPoint
 */
Map.prototype.tileAt = function(hexPoint) {
    // check point is on map
    if (!this.valid(hexPoint)) {
        throw new Error(hexPoint + ' is not on the map');
    }

    return this.tiles[hexPoint.x][hexPoint.y];
}

/**
 * returns the terrain at hexPoint
 *
 * @param {HexPoint} hexPoint point to return the terrain for
 * @return {TerrainType} at hexPoint
 */
Map.prototype.terrainAt = function(hexPoint) {
    // check point is on map
    if (!this.valid(hexPoint)) {
        throw new Error(hexPoint + ' is not on the map');
    }

    return this.tiles[hexPoint.x][hexPoint.y].terrainType;
}

/**
 * modifies the terrain at hexPoint
 *
 * @param {TerrainType} terrainType new terrainType
 * @param {HexPoint} hexPoint point to modify the terrain
 */
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

/**
 * returns the feature at hexPoint
 *
 * @param {HexPoint} hexPoint point to return the feature for
 * @return {FeatureType} at hexPoint
 */
Map.prototype.featureAt = function(hexPoint) {
    // check point is on map
    if (!this.valid(hexPoint)) {
        throw new Error(hexPoint + ' is not on the map');
    }

    return this.tiles[hexPoint.x][hexPoint.y].featureType;
}

/**
 * modifies the feature at hexPoint
 *
 * @param {FeatureType} featureType new featureType
 * @param {HexPoint} hexPoint point to modify the terrain
 */
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

/**
 * returns the resource at hexPoint
 *
 * @param {HexPoint} hexPoint point to return the resource for
 * @return {ResourceType} at hexPoint
 */
Map.prototype.resourceAt = function(hexPoint) {
    // check point is on map
    if (!this.valid(hexPoint)) {
        throw new Error(hexPoint + ' is not on the map');
    }

    return this.tiles[hexPoint.x][hexPoint.y].resourceType;
}

/**
 * modifies the resource at hexPoint
 *
 * @param {ResourceType} resourceType new resourceType
 * @param {HexPoint} hexPoint point to modify the resource
 */
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