/**
 * Unit - Provides unit objects
 *
 * Copyright (c) 2023 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

 import { HexPoint } from './../base/point.js';

// UnitType Constructor

function UnitType(name, max_moves, texture) {
    this.name = name;
    this.max_moves = max_moves;
    this.texture = texture;
}

UnitType.prototype.clone = function() {
    return new UnitType(this.name, this.max_moves, this.texture);
}

UnitType.fromString = function(unit_name) {
    switch (unit_name) {
        case 'none':
            return UnitTypes.none.clone();

        // civilian
        case 'settler':
            return UnitTypes.settler.clone();
        case 'builder':
            return UnitTypes.builder.clone();

        // recon
        case 'scout':
            return UnitTypes.scout.clone();

        // melee
        case 'warrior':
            return UnitTypes.warrior.clone();

        default:
            console.log('could not find Unit for ' + unit_name)
            return UnitTypes.none.clone();
    }
}

const UnitTypes = {
	none: new UnitType("none", 0, "unit-scout@3x.png"),

	// civilian
	settler: new UnitType("settler", 2, "unit-settler@3x.png"),
	builder: new UnitType("builder", 2, "unit-builder@3x.png"),

    // recon
    scout: new UnitType("scout", 3, "unit-scout@3x.png"),

	// melee
	warrior: new UnitType("warrior", 2, "unit-warrior@3x.png"),
}

// Unit Constructor

function Unit() {

    this.name = "";
    this.location = new HexPoint();
    this.unitType = UnitTypes.none;
    this.player = -1;
	this.health = 0;
	this.moves = 0;
}

// Map Object Public Methods

Unit.prototype.fromJson = function(json_dict) {

    this.name = json_dict['name'];
    this.location.x = json_dict['x'];
	this.location.y = json_dict['y'];
	this.unitType = UnitType.fromString(json_dict['unitType']);
	this.player = json_dict['player'];
	this.health = json_dict['health'];
	this.moves = json_dict['moves'];

	/**
	"name": "Settler",
    "x": 19,
    "y": 3,
    "unitType": "settler",
    "greatPerson": null,
    "player": 1092765405,
    "health": 100
    */

	console.log('Unit ' + this.location.x + ', ' + this.location.y + ' => ' + this.unitType);
}

Unit.prototype.toString = function() {
    return "Unit(" + this.name + ", at: " + this.location + ", of: " + this.player + ", at: " + this.health + ")";
}

export { Unit, UnitTypes, UnitType };
