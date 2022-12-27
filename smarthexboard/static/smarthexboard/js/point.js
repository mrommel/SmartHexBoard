/**
 * HexPoint, HexDirection - Provides hex objects
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

function HexPoint(x, y) {
    if (typeof (x) == 'undefined' && typeof (y) == 'undefined') {
        this.x = 0;
	    this.y = 0;
    } else {
	    this.x = x;
	    this.y = y;
	}
}

// HexPoint Object Public Methods

HexPoint.prototype.copy = function(pt) {
    this.x = pt.x;
	this.y = pt.y;
}

HexPoint.prototype.fromHexCube = function(hexCube) {
    // even-q
    this.x = hexCube.q + (hexCube.s + (hexCube.s & 1)) / 2;
    this.y = hexCube.s;

    // self.init(x: cube.q + (cube.s - (cube.s&1)) / 2, y: cube.s) // odd-q
}

HexPoint.prototype.toString = function() {
  return '[HexPoint x: ' + this.x + ', y: ' + this.y + ']';
}

const HexDirections = {
	north: Symbol("north"),
	northEast: Symbol("northEast"),
	southEast: Symbol("southEast"),
	south: Symbol("south"),
	southWest: Symbol("southWest"),
	northWest: Symbol("northWest"),

    /*
    public var opposite: HexDirection {

        switch self {
        case .north:
            return .south
        case .northeast:
            return .southwest
        case .southeast:
            return .northwest
        case .south:
            return .north
        case .southwest:
            return .northeast
        case .northwest:
            return .southeast
        }
    }

    var clockwiseNeighbor: HexDirection {

        switch self {
        case .north:
            return .northeast
        case .northeast:
            return .southeast
        case .southeast:
            return .south
        case .south:
            return .southwest
        case .southwest:
            return .northwest
        case .northwest:
            return .north
        }
    }

    var counterClockwiseNeighbor: HexDirection {

        switch self {
        case .north:
            return .northwest
        case .northeast:
            return .north
        case .southeast:
            return .northeast
        case .south:
            return .southeast
        case .southwest:
            return .south
        case .northwest:
            return .southwest
        }
    }
    */
}

function HexCube(q, r, s) {
	this.q = q;
	this.r = r;
	this.s = s;
}

HexCube.prototype.fromHexPoint = function(hex) {
    // even-q
    this.q = hex.x - (hex.y + (hex.y&1)) / 2;
    this.s = hex.y;
    this.r = -this.q - this.s

    // self.init(q: hex.x - (hex.y - (hex.y&1)) / 2, s: hex.y) // odd-q
}

HexCube.prototype.distanceTo = function(hexCube) {
    return Math.max(Math.abs(this.q - hexCube.q), Math.abs(this.r - hexCube.r), Math.abs(this.s - hexCube.s));
}

HexCube.prototype.add = function(rightHexCube) {
    return HexCube(this.q + rightHexCube.q, this.r + rightHexCube.r, this.s + rightHexCube.s);
}

HexCube.prototype.mul = function(factor) {
    return HexCube(this.q * factor, this.r * factor, this.s * factor);
}

HexCube.prototype.toString = function() {
  return '[HexCube q: ' + this.q + ', r: ' + this.r + ', s: ' + this.s + ']';
}