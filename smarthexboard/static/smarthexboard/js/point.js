/**
 * HexPoint, HexDirection - Provides hex objects
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

function HexOrientation() {
    this.f0 = 3.0 / 2.0;
    this.f1 = 0.0;
    this.f2 = Math.sqrt(3.0) / 2.0;
    this.f3 = Math.sqrt(3.0);
    this.b0 = 2.0 / 3.0;
    this.b1 = 0.0;
    this.b2 = -1.0 / 3.0;
    this.b3 = Math.sqrt(3.0) / 3.0;
    this.startAngle = 0.0;
}

function HexLayout() {
    this.orientation = new HexOrientation();
    this.size = new CGSize(36.0, 26.0);
    this.origin = new CGPoint(250.0, 450.0);
}

HexLayout.prototype.toHex = function(screenPoint) {
    var point = new CGPoint((screenPoint.x - this.origin.x) / this.size.width, (screenPoint.y - this.origin.y) / this.size.height);
    var q = this.orientation.b0 * point.x + this.orientation.b1 * point.y;
    var r = this.orientation.b2 * point.x + this.orientation.b3 * point.y;
    var s = -q - r;

    return new HexCube(q, r, s);
}

HexLayout.prototype.toScreen = function(hexCube) {
    // console.log('HexLayout.toScreen(' + hexCube + ')');
    var x = (this.orientation.f0 * hexCube.q + this.orientation.f1 * hexCube.r) * this.size.width;
    var y = (this.orientation.f2 * hexCube.q + this.orientation.f3 * hexCube.r) * this.size.height;

    return new CGPoint(x + this.origin.x, y + this.origin.y);
}

var layout = new HexLayout();

// HexPoint Constructor

function HexPoint(x, y) {
    if (x instanceof HexCube && typeof (y) == 'undefined') {
        // construct HexPoint from HexCube
        var hexCube = x;
        this.x = hexCube.q + (hexCube.s + (hexCube.s & 1)) / 2;
        this.y = hexCube.s;
    } else if (x instanceof CGPoint && typeof (y) == 'undefined') {
        // construct HexPoint from screen Point: CGPoint
        var screenPoint = x;
        var hexCube = new HexCube(screenPoint);
        // console.log('hexCube=' + hexCube);
        this.x = hexCube.q + (hexCube.s + (hexCube.s & 1)) / 2;
        this.y = hexCube.s;
    } else if (typeof (x) == 'undefined' && typeof (y) == 'undefined') {
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

    // odd-q
    // this.x = hexCube.q + (hexCube.s - (hexCube.s & 1)) / 2;
    // this.y = hexCube.s)
}

HexPoint.prototype.toScreen = function() {
    var hexCube = new HexCube(this);
    // console.log('HexPoint.toScreen=' + hexCube);
    return hexCube.toScreen();
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
    if (q instanceof HexPoint && typeof (r) == 'undefined' && typeof (s) == 'undefined') {
        var hex = q;
        this.q = hex.x - (hex.y + (hex.y&1)) / 2;
        this.s = hex.y;
        this.r = -this.q - this.s
    } else if (q instanceof CGPoint && typeof (r) == 'undefined' && typeof (s) == 'undefined') {
        var screenPoint = q;
        var hexCube = layout.toHex(screenPoint);

        this.q = hexCube.q;
        this.s = hexCube.s;
        this.r = hexCube.r;
    } else {
	    this.q = q;
	    this.r = r;
	    this.s = s;
	}
}

HexCube.prototype.fromHexPoint = function(hex) {
    // even-q
    this.q = hex.x - (hex.y + (hex.y&1)) / 2;
    this.s = hex.y;
    this.r = -this.q - this.s

    // odd-q
    // self.init(q: hex.x - (hex.y - (hex.y&1)) / 2, s: hex.y)
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

HexCube.prototype.toScreen = function() {
    return layout.toScreen(this);
}

HexCube.prototype.toString = function() {
  return '[HexCube q: ' + this.q + ', r: ' + this.r + ', s: ' + this.s + ']';
}