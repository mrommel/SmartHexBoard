/**
 * Map - Provides map, player and hex objects
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

import { Perlin } from './perlin.js';

// HeightMap Constructor

function HeightMap(cols, rows) {

    if (typeof (cols) == 'undefined' && typeof (rows) == 'undefined') {
        this.cols = 10;
	    this.rows = 10;
    } else {
	    this.cols = cols;
	    this.rows = rows;
	}

	this.values = Array(this.cols).fill().map(()=>Array(this.rows).fill());

	for (var i = 0; i < this.cols; i++) {
        for (var j = 0; j < this.rows; j++) {
            this.values[i][j] = 0.0;
        }
    }
}

/**
 * generates the heightmap
 */
HeightMap.prototype.generate = function() {

    var perlin = new Perlin();
    perlin.seed(Math.random());

    var zoom = 0.125;

    for (var x = 0; x < this.cols; x++) {
        for (var y = 0; y < this.rows; y++) {

            var nx = zoom * x;
            var ny = zoom * y;

            var value0 = 1.0 * perlin.simplex2(1.0 * nx, 1.0 * ny);
            var value1 = 0.25 * (perlin.simplex2(nx + 1, ny) + perlin.simplex2(nx - 1, ny) + perlin.simplex2(nx, ny + 1) + perlin.simplex2(nx, ny - 1));

            var value = (value0 + value1) / 2.0;
            value = Math.max(Math.min(value, 1.0), -1.0);

            this.values[x][y] = value;
        }
    }

    this.normalize();
}

/**
generates the heightmap based on the input parameters

- parameter octaves: 4
- parameter zoom: 1.0
- parameter persistence: 1.0
*/
HeightMap.prototype.percentageBelow = function(threshold) {

    var num_below = 0;
    var num_all = 0;

    for (var x = 0; x < this.cols; x++) {
        for (var y = 0; y < this.rows; y++) {
            if (this.values[x][y] < threshold) {
                num_below += 1.0
            }
            num_all += 1.0
        }
    }

    return num_below / num_all;
}

HeightMap.prototype.normalize = function() {

    var maxValue = -Number.MAX_VALUE;
    var minValue = Number.MAX_VALUE;

    // find min / max
    for (var x = 0; x < this.cols; x++) {
        for (var y = 0; y < this.rows; y++) {
            maxValue = Math.max(maxValue, this.values[x][y]);
            minValue = Math.min(minValue, this.values[x][y]);
        }
    }

    // scale
    for (var x = 0; x < this.cols; x++) {
        for (var y = 0; y < this.rows; y++) {
            this.values[x][y] = (this.values[x][y] - minValue) / (maxValue - minValue);
        }
    }
}

HeightMap.prototype.findThresholdAbove = function(percentage) {

    var tmpArray = []

    // fill from map
    for (var x = 0; x < this.cols; x++) {
        for (var y = 0; y < this.rows; y++) {
            tmpArray.push(this.values[x][y]);
        }
    }

    // sorted smallest first, highest last
    tmpArray.sort();
    tmpArray.reverse();

    var thresholdIndex = Math.floor(tmpArray.length * percentage);
    console.log('thresholdIndex=' + thresholdIndex);

    return tmpArray[thresholdIndex - 1];
}

export { HeightMap };