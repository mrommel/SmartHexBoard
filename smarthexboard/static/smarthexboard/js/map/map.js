/**
 * Map - Provides map, player and hex objects
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

import { HexPoint } from '../base/point.js';
import { CGSize, CGPoint } from '../base/prototypes.js';
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

Map.prototype.fromJson = function(json_dict) {

    this.cols = json_dict['width'];
	this.rows = json_dict['height'];

	this.tiles = Array(this.cols).fill().map(()=>Array(this.rows).fill());

    for (var j = 0; j < this.rows; j++) {
	    for (var i = 0; i < this.cols; i++) {
	        const terrain_name = json_dict['tiles']['values']['' + j][i]['terrain'];
	        const terrain_type = TerrainType.fromString(terrain_name);
            console.log('terrain: ' + terrain_type);
            this.tiles[i][j] = new Tile(terrain_type);
        }
    }

    this.units = []
    this.cities = []
}

Map.prototype.copy = function(map) {
    this.rows = map.rows;
	this.cols = map.cols;

	this.tiles = map.tiles.map(function(arr) {
        return arr.slice();
    });

    // @todo: copy cities, units
}

Map.prototype.canvasSize = function() {
    var pt0 = new HexPoint(0, 0).toScreen();
    var pt1 = new HexPoint(this.cols, 0).toScreen();
    var pt2 = new HexPoint(0, this.rows).toScreen();
    var pt3 = new HexPoint(this.cols, this.rows).toScreen();

    var min_x = Math.min(Math.min(pt0.x, pt1.x), Math.min(pt2.x, pt3.x));
    var max_x = Math.max(Math.max(pt0.x, pt1.x), Math.max(pt2.x, pt3.x));

    var min_y = Math.min(Math.min(pt0.y, pt1.y), Math.min(pt2.y, pt3.y));
    var max_y = Math.max(Math.max(pt0.y, pt1.y), Math.max(pt2.y, pt3.y));

    // console.log('size minx: ' + minx + ', maxx: ' + maxx);
    // console.log('size miny: ' + miny + ', maxy: ' + maxy);

    return new CGSize(max_x - min_x + 16, max_y - min_y);
}

Map.prototype.canvasOffset = function() {
    var pt0 = new HexPoint(0, 0).toScreen();
    var pt1 = new HexPoint(this.cols, 0).toScreen();
    var pt2 = new HexPoint(0, this.rows).toScreen();
    var pt3 = new HexPoint(this.cols, this.rows).toScreen();

    var min_y = Math.min(Math.min(pt0.y, pt1.y), Math.min(pt2.y, pt3.y));
    var max_y = Math.max(Math.max(pt0.y, pt1.y), Math.max(pt2.y, pt3.y));
    var content_y = max_y - min_y;

    console.log('offset x: ' + pt0.x + ', y: ' + (content_y - pt0.y));

    return new CGPoint(pt0.x + 52, content_y - pt0.y);
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
 * returns if the tile at hexPoint is coastal - on land and adjacent to water
 *
 * @param {HexPoint} hexPoint point to return if the land! tile is coastal for
 * @return {Boolean} if the tile at hexPoint is coastal
 */
Map.prototype.isCoastalAt = function(hexPoint) {

    // console.log('Debug: isCoastalAt(' + hexPoint + ') - isWater: ' + this.terrainAt(hexPoint).isWater());

    // we are only coastal if we are on land
    if (this.terrainAt(hexPoint).isWater()) {
        return false;
    }

    for (const neighborPoint of hexPoint.neighbors()) {

        if (!this.valid(neighborPoint)) {
            continue;
        }

        const neighborTerrain = this.terrainAt(neighborPoint);
        console.log('Debug: neighbor ' + neighborPoint + ' has ' + neighborTerrain);

        if (neighborTerrain.isWater()) {
            return true;
        }
    }

    return false;
}

Map.prototype.isHillsAt = function(hexPoint) {
    // check point is on map
    if (!this.valid(hexPoint)) {
        throw new Error(hexPoint + ' is not on the map');
    }

    return this.tiles[hexPoint.x][hexPoint.y].isHills;
}

Map.prototype.modifyHillsAt = function(isHills, hexPoint) {
    // check point is on map
    if (!this.valid(hexPoint)) {
        throw new Error(hexPoint + ' is not on the map');
    }

    this.tiles[hexPoint.x][hexPoint.y].isHills = isHills;
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

Map.prototype.climateZoneAt = function(hexPoint) {
    // check point is on map
    if (!this.valid(hexPoint)) {
        throw new Error(hexPoint + ' is not on the map');
    }

    return this.tiles[hexPoint.x][hexPoint.y].climateZone;
}

Map.prototype.modifyClimateZoneAt = function(climateZone, hexPoint) {
    // check point is on map
    if (!this.valid(hexPoint)) {
        throw new Error(hexPoint + ' is not on the map');
    }

    this.tiles[hexPoint.x][hexPoint.y].climateZone = climateZone;
}

Map.prototype.toString = function() {
    return '[Map: ' + this.cols + 'x' + this.rows + ']';
}

export { Tile, Map };