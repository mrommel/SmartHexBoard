/**
 * Map Generator - Provides new maps
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

import { HexPoint } from '../base/point.js';
import { TerrainType, TerrainTypes, FeatureType, FeatureTypes, ResourceType, ResourceTypes, MapSize, MapSizes } from './types.js';
import { Tile } from './tile.js';
import { HeightMap } from './heightmap.js';
import { Map } from './map.js';

// MapType Constructor

function MapType(name) {
    this.name = name;
}

MapType.prototype.clone = function() {
    return new MapType(this.name);
}

MapType.prototype.toString = function() {
    return '[MapType: ' + this.name + ']';
}

const MapTypes = {
	empty: new MapType("empty"),
	earth: new MapType("earth"),
	pangaea: new MapType("pangaea"),
	continents: new MapType("continents"),
    // case archipelago
    // case inlandsea
}


// MapOptions

/**
 * creates a new MapOptions object
 *
 * @param {MapSize} mapSize size class of the map
 * @param {MapType} mapType type class of the map
 * @return map options
 */
function MapOptions(mapSize, mapType) {

    if (typeof (mapSize) == 'undefined') {
        this.size = MapSizes.duel;
    } else {
        this.size = mapSize;
    }

    if (typeof (mapType) == 'undefined') {
        this.type = MapTypes.empty;
    } else {
        this.type = mapType;
    }
}

// MapGenerator Constructor

/**
 * creates a new MapGenerator object
 *
 * @param {MapOptions} options size class of the map
 * @return map generator
 */
function MapGenerator(options) {

    this.options = options
}

// MapGenerator Object Public Methods

MapGenerator.prototype.generate = function(callbackFunction) {

    console.log('MapGenerator - start creating map with: ' + this.options.size + ' and ' + this.options.type);

    if (callbackFunction) {
        callbackFunction('started creating map with ' + this.options.size.cols + 'x' + this.options.size.rows, 0.0, null);
    }

    var map = new Map(this.options.size.cols, this.options.size.rows);

    var heightmap = new HeightMap(this.options.size.cols, this.options.size.rows);
    heightmap.generate();

    // console.log(heightmap);
    var threshold = heightmap.findThresholdAbove(0.40);
    console.log('threshold=' + threshold);

    for (var i = 0; i < this.options.size.cols; i++) {
        for (var j = 0; j < this.options.size.rows; j++) {

            if (heightmap.values[i][j] > threshold) {
                // console.log('below zero at ' + new HexPoint(i, j));
                map.modifyTerrainAt(TerrainTypes.grass, new HexPoint(i, j));
            } else {
                // console.log('above zero at ' + new HexPoint(i, j));
                map.modifyTerrainAt(TerrainTypes.ocean, new HexPoint(i, j));
            }
        }
    }

    map.modifyTerrainAt(TerrainTypes.grass, new HexPoint(1, 2));
    map.modifyResourceAt(ResourceTypes.whales, new HexPoint(4, 2));
    map.modifyFeatureAt(FeatureTypes.forest, new HexPoint(3, 3));

    if (callbackFunction) {
        callbackFunction('finished', 1.0, map);
    }
}

export { MapType, MapOptions, MapGenerator };