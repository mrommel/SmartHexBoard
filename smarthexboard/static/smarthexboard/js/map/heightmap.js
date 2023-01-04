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
generates the heightmap based on the input parameters

- parameter octaves: 4
- parameter zoom: 1.0
- parameter persistence: 1.0
*/
HeightMap.prototype.generate = function(octaves, zoom, persistence) {

    var perlin = new Perlin();
    perlin.seed(Math.random());

    /*generator.octaves = octaves
    generator.zoom = zoom
    generator.persistence = persistence*/
    const tau = 2.0 * Math.PI;

    for (var x = 0; x < this.cols; x++) {
        for (var y = 0; y < this.rows; y++) {

            var nx = (x + 0.0) / this.cols - 0.5;
            var ny = (y + 0.0) / this.rows - 0.5;

            var angle_x = tau * nx;

            /* In "noise parameter space", we need nx and ny to travel the
                   same distance. The circle created from nx needs to have
                   circumference=1 to match the length=1 line created from ny,
                   which means the circle's radius is 1/2π, or 1/tau */

            // self[x, y] = generator.perlinNoise(x: cos(angle_x) / self.tau, y: sin(angle_x) / self.tau, z: ny, t: 0)

            /*var value0 = 1.00 * perlin.noise(1.0 * Math.cos(angle_x) / tau, 1.0 * Math.sin(angle_x) / tau); //, z: 1.0 * ny)
            var value1 = 0.50 * perlin.noise(2.0 * Math.cos(angle_x) / tau, 2.0 * Math.sin(angle_x) / tau); //, z: 2.0 * ny)
            var value2 = 0.25 * perlin.noise(4.0 * Math.cos(angle_x) / tau, 4.0 * Math.sin(angle_x) / tau); //, z: 4.0 * ny)
            var value3 = 0.125 * perlin.noise(8.0 * Math.cos(angle_x) / tau, 8.0 * Math.sin(angle_x) / tau); //, z: 8.0 * ny)

            var value = Math.abs(value0 + value1 + value2 + value3) / 1.875;
            if (value > 1.0) {
                value = 1.0;
            }

            this.values[x][y] = Math.pow(value, 4.0); // 1.97*/
            this.values[x][y] = perlin.simplex2(x, y);
        }
    }
}

export { HeightMap };