/**
 * Map Generator - Provides new maps
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

import { HexPoint, HexDirections } from '../base/point.js';
import { TerrainType, TerrainTypes, GenerationTypes, FeatureType, FeatureTypes, ResourceType, ResourceTypes, MapSize, MapSizes, ClimateZones } from './types.js';
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
        // TXT_KEY_MAP_GENERATOR_INIT
        callbackFunction('started creating map with ' + this.options.size.cols + 'x' + this.options.size.rows, 0.0, null);
    }

    var grid = new Map(this.options.size.cols, this.options.size.rows);

    var heightMap = new HeightMap(this.options.size.cols, this.options.size.rows);
    heightMap.generate();

    var moistureMap = new HeightMap(this.options.size.cols, this.options.size.rows);
    moistureMap.generate();

    // 1st step: land / water
    var threshold = heightMap.findThresholdAbove(0.40); // 40% is land
    this.fillFromElevation(grid, heightMap, threshold);

    if (callbackFunction) {
		callbackFunction("TXT_KEY_MAP_GENERATOR_ELEVATION", 0.3, null);
	}

	// 2nd step: climate
    var climateZones = this.initClimateZones();

    if (callbackFunction) {
        callbackFunction("TXT_KEY_MAP_GENERATOR_CLIMATE", 0.35, null);
    }

    // 2.1nd step: refine climate based on cost distance
    var distanceToCoast = this.prepareDistanceToCoast(grid);
    this.refineClimate(climateZones, distanceToCoast);

    if (callbackFunction) {
        callbackFunction("TXT_KEY_MAP_GENERATOR_COASTAL", 0.4, null);
    }

    // 3rd step: refine terrain
    this.refineTerrain(grid, heightMap, moistureMap, climateZones);
    this.blendTerrains(grid);

    if (callbackFunction) {
        callbackFunction("TXT_KEY_MAP_GENERATOR_TERRAIN", 0.5, null);
    }
    /*
    self.placeResources(on: grid)

    if (callbackFunction) {
        callbackFunction("TXT_KEY_MAP_GENERATOR_RESOURCES", 0.6, null);
    }

    // 4th step: rivers
    self.placeRivers(number: options.rivers, on: grid, with: heightMap);

    if (callbackFunction) {
        callbackFunction("TXT_KEY_MAP_GENERATOR_RIVERS", 0.7, null);
    }

    // 5th step: features
    self.refineFeatures(on: grid);

    if (callbackFunction) {
        callbackFunction("TXT_KEY_MAP_GENERATOR_FEATURES", 0.75, null);
    }

    // 6th step: features
    self.refineNaturalWonders(on: grid);

    if (callbackFunction) {
        callbackFunction("TXT_KEY_MAP_GENERATOR_NATURAL_WONDERS", 0.8, null);
    }

    // 7th step: continents & oceans
    self.identifyContinents(on: grid)

    if (callbackFunction) {
        callbackFunction("TXT_KEY_MAP_GENERATOR_CONTINENTS", 0.85, null);
    }

    self.identifyOceans(on: grid)

    if (callbackFunction) {
        callbackFunction("TXT_KEY_MAP_GENERATOR_OCEANS", 0.9, null);
    }

    self.identifyStartPositions(on: grid)

    if (callbackFunction) {
        callbackFunction("TXT_KEY_MAP_GENERATOR_POSITIONS", 0.95, null);
    }

    self.addGoodyHuts(on: grid)

    if (callbackFunction) {
        callbackFunction("TXT_KEY_MAP_GENERATOR_GOODIES", 0.99, null);
    }
    */

    //
    // grid.modifyResourceAt(ResourceTypes.whales, new HexPoint(4, 2));
    // grid.modifyFeatureAt(FeatureTypes.forest, new HexPoint(3, 3));

    if (callbackFunction) {
        callbackFunction('finished', 1.0, grid);
    }
}

MapGenerator.prototype.fillFromElevation = function(grid, heightmap, threshold) {

    for (var i = 0; i < this.options.size.cols; i++) {
        for (var j = 0; j < this.options.size.rows; j++) {

            if (heightmap.values[i][j] > threshold) {
                grid.modifyTerrainAt(GenerationTypes.land, new HexPoint(i, j));
            } else {
                grid.modifyTerrainAt(GenerationTypes.water, new HexPoint(i, j));
            }
        }
    }
}

// MARK: 2nd step methods
MapGenerator.prototype.initClimateZones = function() {

    var climateZones = Array(this.options.size.cols).fill().map(()=>Array(this.options.size.rows).fill());

	for (var i = 0; i < this.options.size.cols; i++) {
        for (var j = 0; j < this.options.size.rows; j++) {
            climateZones[i][j] = ClimateZones.temperate;
        }
    }

    for (var x = 0; x < this.options.size.cols; x++) {
        for (var y = 0; y < this.options.size.rows; y++) {

            const latitude = Math.abs(this.options.size.rows / 2.0 - y) / (this.options.size.rows / 2.0);

            if (latitude > 0.9 || y == 0 || y == (this.options.size.rows - 1)) {
                climateZones[x][y] = ClimateZones.polar;
            } else if (latitude > 0.65) {
                climateZones[x][y] = ClimateZones.sub_polar;
            } else if (latitude > 0.4) {
                climateZones[x][y] = ClimateZones.temperate;
            } else if (latitude > 0.2) {
                climateZones[x][y] = ClimateZones.sub_tropic;
            } else {
                climateZones[x][y] = ClimateZones.tropic;
            }
        }
    }

    return climateZones;
}

MapGenerator.prototype.prepareDistanceToCoast = function(grid) {

    if (!(grid instanceof Map)) {
        throw new Error('grid is not a Map');
    }

    var distanceToCoast = Array(this.options.size.cols)
        .fill()
        .map(()=>Array(this.options.size.rows).fill());

	for (var i = 0; i < this.options.size.cols; i++) {
        for (var j = 0; j < this.options.size.rows; j++) {
            distanceToCoast[i][j] = Number.MAX_VALUE;
        }
    }

    var actionHappened = true;
    while (actionHappened) {

        // reset
        actionHappened = false;

        for (var x = 0; x < this.options.size.cols; x++) {
            for (var y = 0; y < this.options.size.rows; y++) {

                // this needs to be analyzed
                if (distanceToCoast[x][y] == Number.MAX_VALUE) {

                    // if field is ocean => no distance
                    // console.log(grid);
                    if (grid.tiles[x][y] == GenerationTypes.water) {
                        distanceToCoast[x][y] = 0;
                        actionHappened = true;
                    } else {
                        // check neighbors
                        var distance = Number.MAX_VALUE;
                        var point = new HexPoint(x, y);
                        var _this = this; // context this is not visible on forEach loop
                        Object.values(HexDirections).forEach(function(direction) {

                            const neighbor = point.neighborIn(direction, 1);
                            if (neighbor.x >= 0 &&
                                neighbor.x < _this.options.size.cols &&
                                neighbor.y >= 0 &&
                                neighbor.y < _this.options.size.rows) {

                                if (distanceToCoast[x][y] != Number.MAX_VALUE) {
                                    distance = Math.min(distance, distanceToCoast[x][y] + 1);
                                }
                            }
                        });

                        if (distance < Number.MAX_VALUE) {
                            distanceToCoast[x][y] = distance;
                            actionHappened = true;
                        }
                    }
                }
            }
        }
    }

    return distanceToCoast;
}

MapGenerator.prototype.refineClimate = function(climateZones, distanceToCoast) {

    for (var x = 0; x < this.options.size.cols; x++) {
        for (var y = 0; y < this.options.size.rows; y++) {

            const distance = distanceToCoast[x][y];

            if (distance < 2) {
                switch (climateZones[x][y]) {
                    case ClimateZones.polar:
                        climateZones[x][y] = ClimateZones.sub-polar;
                    case ClimateZones.sub-polar:
                        climateZones[x][y] = ClimateZones.temperate;
                    case ClimateZones.temperate:
                        climateZones[x][y] = ClimateZones.sub-tropic;
                    case ClimateZones.sub-tropic:
                        climateZones[x][y] = ClimateZones.tropic;
                    case ClimateZones.tropic:
                        climateZones[x][y] = ClimateZones.tropic;
                }
            }
        }
    }
}

// MARK: 3rd step methods

MapGenerator.prototype.refineTerrain = function(grid, heightMap, moistureMap, climateZones) {

    var landPlots = 0;

    for (var x = 0; x < this.options.size.cols; x++) {
        for (var y = 0; y < this.options.size.rows; y++) {
            const gridPoint = new HexPoint(x, y);

            if (grid.terrainAt(gridPoint) == GenerationTypes.water) {

                // check is next continent
                var nextToContinent = gridPoint
                    .neighbors()
                    .map(neighbor => {
                        return grid.valid(neighbor) && grid.terrainAt(neighbor).isLand();
                    })
                    .reduce(
                        (previousValue, currentValue) => previousValue || currentValue,
                        false
                    );

                if (heightMap.values[x][y] > 0.4 || nextToContinent) {
                    grid.modifyTerrainAt(TerrainTypes.shore, gridPoint);
                } else {
                    grid.modifyTerrainAt(TerrainTypes.ocean, gridPoint);
                }
            } else {
                landPlots += 1

                this.updateBiome(gridPoint, grid, heightMap.values[x][y], moistureMap.values[x][y], climateZones[x][y]);
            }

            grid.modifyClimateZoneAt(climateZones[x][y], gridPoint);
        }
    }

    // make all ocean tiles directly adjacent to land as shore
    /*for (var x = 0; x < this.options.size.cols; x++) {
        for (var y = 0; y < this.options.size.rows; y++) {
            const gridPoint = new HexPoint(x, y);

            if (grid.terrainAt(gridPoint) == TerrainTypes.ocean) {
                var shouldBeShore = false;

                for (const neighborPoint in gridPoint.neighbors()) {

                    if (grid.isValid(neighborPoint)) {
                        continue;
                    }

                    const neighborTerrain = grid.terrainAt(neighborPoint);

                    if (!neighborTerrain.isWater()) {
                        shouldBeShore = true;
                        break;
                    }
                }

                if (shouldBeShore) {
                    grid.modifyTerrainAt(TerrainTypes.shore, gridPoint);
                }
            }
        }
    }*/

    // Expanding coasts (MapGenerator.Lua)
    // Chance for each eligible plot to become an expansion is 1 / iExpansionDiceroll.
    // Default is two passes at 1/4 chance per eligible plot on each pass.
    /*for _ in 0..<2 {
        var shallowWaterPlots: [HexPoint] = []
        for x in 0..<width {
            for y in 0..<height {
                let gridPoint = HexPoint(x: x, y: y)

                if grid.terrain(at: gridPoint) == .ocean {
                    var isAdjacentToShallowWater: Bool = false
                    for neighbor in gridPoint.neighbors() {

                        guard let neighborTile = grid.tile(at: neighbor) else {
                            continue
                        }

                        if neighborTile.terrain() == .shore && Int.random(number: 5) == 0 {
                            isAdjacentToShallowWater = true
                            break
                        }
                    }

                    if isAdjacentToShallowWater {
                        shallowWaterPlots.append(gridPoint)
                    }
                }
            }
        }

        for shallowWaterPlot in shallowWaterPlots {
            grid.set(terrain: .shore, at: shallowWaterPlot)
        }
    }*/

    // get highest percent tiles from height map
    const combinedPercentage = this.options.mountainsPercentage * this.options.landPercentage;
    const mountainThreshold = heightMap.findThresholdAbove(combinedPercentage);

    var numberOfMountains = 0;

    for (var x = 0; x < this.options.size.cols; x++) {
        for (var y = 0; y < this.options.size.rows; y++) {
            const gridPoint = new HexPoint(x, y);

            if (heightMap.values[gridPoint.x][gridPoint.y] >= mountainThreshold) {
                grid.modifyFeatureAt(FeatureTypes.mountains, gridPoint);
                numberOfMountains += 1;
            }
        }
    }

    // remove some mountains, where there are mountain neighbors
    /*let points = grid.points().shuffled

    for gridPoint in points {

        var mountainNeighbors = 0
        var numberNeighbors = 0

        for neighbor in gridPoint.neighbors() {

            guard let neighborTile = grid.tile(at: neighbor) else {
                continue
            }

            if neighborTile.feature() == .mountains || neighborTile.feature() == .mountEverest || neighborTile.feature() == .mountKilimanjaro {
                mountainNeighbors += 1
            }

            numberNeighbors += 1
        }

        if (numberNeighbors == 6 && mountainNeighbors >= 5) || (numberNeighbors == 5 && mountainNeighbors >= 4) {
            grid.set(feature: .none, at: gridPoint)
            print("mountain removed")
        }
    }*/

    // print("Number of Mountains: \(numberOfMountains)")
}

MapGenerator.prototype.blendTerrains = function(grid) {

    // mglobal.hillsBlendPercent        = 0.45 -- Chance for flat land to become hills per near mountain. Requires at least 2 near mountains.
    const terrainBlendRange = 3;       // range to smooth terrain (desert surrounded by plains turns to plains, etc)
    const terrainBlendRandom = 0.6;  // random modifier for terrain smoothing

    /*let points = grid.points().shuffled

    for pt in points {

        if tile.isWater() {
            continue
        }

        const plotPercents = grid.plotStatistics(at: pt, radius: terrainBlendRange)
        const randPercent = 1.0 + Double.random * 2.0 * terrainBlendRandom - terrainBlendRandom;

        if tile.feature() == .mountains {

            var numNearMountains = 0

            for neighbor in tile.point.neighbors() {

                guard let neighborTile = grid.tile(at: neighbor) else {
                    continue
                }

                if neighborTile.feature() == .mountains {
                    numNearMountains += 1
                }
            }

            if 2 <= numNearMountains && numNearMountains <= 4 {
                self.createPossibleMountainPass(at: tile.point, on: gridRef)
            }
        } else {

            if tile.terrain() == .grass {
                if plotPercents.desert + plotPercents.snow >= 0.33 * randPercent {
                    tile.set(terrain: .plains)
                    if tile.feature() == .marsh {
                        tile.set(feature: .forest)
                    }
                }
            } else if tile.terrain() == .plains {
                if plotPercents.desert >= 0.5 * randPercent {
                     // plot:SetTerrainType(TerrainTypes.TERRAIN_DESERT, true, true)
                }
            } else if tile.terrain() == .desert {
                if plotPercents.grass + plotPercents.snow >= 0.25 * randPercent {
                    tile.set(terrain: .plains)
                } / *else if plotPercents.rainforest + plotPercents.MARSH >= 0.25 * randPercent {
                     plot:SetTerrainType(TerrainTypes.TERRAIN_PLAINS, true, true)
                }* /
            } else if tile.feature() == .rainforest && tile.feature() == .marsh {
                if plotPercents.snow + plotPercents.tundra + plotPercents.desert >= 0.25 * randPercent {
                    tile.set(feature: .none)
                }
            } else if tile.terrain() == .tundra {
                if 2.0 * plotPercents.grass + plotPercents.plains + plotPercents.desert >= 0.5 * randPercent {
                    tile.set(terrain: .plains)
                }
            }
        }
    }*/
}

// from http://www.redblobgames.com/maps/terrain-from-noise/
MapGenerator.prototype.updateBiome = function(point, grid, elevation, moisture, climateZone) {

    switch (climateZone) {

    case ClimateZones.polar:
        this.updateBiomeForPolar(point, grid, elevation, moisture);
    case ClimateZones.sub_polar:
        this.updateBiomeForSubpolar(point, grid, elevation, moisture);
    case ClimateZones.temperate:
        this.updateBiomeForTemperate(point, grid, elevation, moisture);
    case ClimateZones.sub_tropic:
        this.updateBiomeForSubtropic(point, grid, elevation, moisture);
    case ClimateZones.tropic:
        this.updateBiomeForTropic(point, grid, elevation, moisture);
    }
}

MapGenerator.prototype.updateBiomeForPolar = function(gridPoint, grid, elevation, moisture) {

    if (Math.random() > 0.5) {
        grid.modifyHillsAt(true, gridPoint);
    }

    grid.modifyTerrainAt(TerrainTypes.snow, gridPoint);
}

MapGenerator.prototype.updateBiomeForSubpolar = function(gridPoint, grid, elevation, moisture) {

    if (elevation > 0.7 && Math.random() > 0.7) {
        grid.modifyHillsAt(true, gridPoint);
        grid.modifyTerrainAt(TerrainTypes.snow, gridPoint);
        return
    }

    if (elevation > 0.5 && Math.random() > 0.6) {
        grid.modifyTerrainAt(TerrainTypes.snow, gridPoint);
        return
    }

    if (Math.random() > 0.85) {
        grid.modifyHillsAt(true, gridPoint);
    }

    grid.modifyTerrainAt(TerrainTypes.tundra, gridPoint);
    return
}

MapGenerator.prototype.updateBiomeForTemperate = function(gridPoint, grid, elevation, moisture) {

    if (elevation > 0.7 && Math.random() > 0.7) {
        grid.modifyHillsAt(true, gridPoint);
        grid.modifyTerrainAt(TerrainTypes.grass, gridPoint);
        return
    }

    if (Math.random() > 0.85) {
        grid.modifyHillsAt(true, gridPoint);
    }

    if (moisture < 0.5) {
        grid.modifyTerrainAt(TerrainTypes.plains, gridPoint);
        return
    } else {
        grid.modifyTerrainAt(TerrainTypes.grass, gridPoint);
        return
    }
}

MapGenerator.prototype.updateBiomeForSubtropic = function(gridPoint, grid, elevation, moisture) {

    if (elevation > 0.7 && Math.random() > 0.7) {
        grid.modifyHillsAt(true, gridPoint);
        grid.modifyTerrainAt(TerrainTypes.plains, gridPoint);
        return
    }

    if (Math.random() > 0.85) {
        grid.modifyHillsAt(true, gridPoint);
    }

    if (moisture < 0.2) {
        if (Math.random() < 0.3) {
            grid.modifyTerrainAt(TerrainTypes.desert, gridPoint);
        } else {
            grid.modifyTerrainAt(TerrainTypes.plains, gridPoint);
        }
    } else if (moisture < 0.6) {
        grid.modifyTerrainAt(TerrainTypes.plains, gridPoint);
    } else {
        grid.modifyTerrainAt(TerrainTypes.grass, gridPoint);
    }
}

MapGenerator.prototype.updateBiomeForTropic = function(gridPoint, grid, elevation, moisture) {

    if (elevation > 0.7 && Math.random() > 0.7) {
        grid.modifyHillsAt(true, gridPoint);
        grid.modifyTerrainAt(TerrainTypes.plains, gridPoint);
        return
    }

    if (Math.random() > 0.85) {
        grid.modifyHillsAt(true, gridPoint);
    }

    // arid
    if (moisture < 0.3) {
        if (Math.random() < 0.4) {
            grid.modifyTerrainAt(TerrainTypes.desert, gridPoint);
        } else {
            grid.modifyTerrainAt(TerrainTypes.plains, gridPoint);
        }
    } else {
        grid.modifyTerrainAt(TerrainTypes.plains, gridPoint);
    }
}

export { MapType, MapOptions, MapGenerator };