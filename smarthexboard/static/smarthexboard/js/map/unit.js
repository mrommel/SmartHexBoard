/**
 * Unit - Provides unit objects
 *
 * Copyright (c) 2023 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

 import { HexPoint } from '../base/point.js';

// UnitType Constructor

function UnitType(name, max_moves, texture, template) {
    this.name = name;
    this.max_moves = max_moves;
    this.texture = texture;
    this.template = template;
}

// UnitType Object Public Methods

UnitType.prototype.mapType = function() {
    switch (this.name) {
        case 'settler':
            return 'civilian';
        case 'builder':
            return 'civilian';

        case 'scout':
            return 'combat';
        case 'warrior':
            return 'combat';
        default:
            console.log('could not find map type for ' + this.name);
            return 'none';
    }
}

UnitType.prototype.clone = function() {
    return new UnitType(this.name, this.max_moves, this.texture, this.template);
}

UnitType.prototype.toString = function() {
    return "UnitType(" + this.name + ", max_moves: " + this.max_moves + ")";
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
	none: new UnitType("none", 0, "unit-scout@3x.png", 'unit-type-template-scout@3x.png'),

	// civilian
	settler: new UnitType("settler", 2, "unit-settler@3x.png", 'unit-type-template-settler@3x.png'),
	builder: new UnitType("builder", 2, "unit-builder@3x.png", 'unit-type-template-builder@3x.png'),

    // recon
    scout: new UnitType("scout", 3, "unit-scout@3x.png", 'unit-type-template-scout@3x.png'),

	// melee
	warrior: new UnitType("warrior", 2, "unit-warrior@3x.png", 'unit-type-template-warrior@3x.png'),
}

// Unit Constructor

function Unit() {

    this.name = "";
    this.location = new HexPoint();
    this.unitType = UnitTypes.none;
    this.player = -1;
	this.health = 0;
	this.moves = 0;

    // strength
    this.meleeStrength = 0;
    this.rangedStrength = 0;
    this.rangedRange = 0;
}

// Unit Object Public Methods

Unit.prototype.fromJson = function(json_dict) {

    this.name = json_dict['name'];
    this.location.x = json_dict['x'];
	this.location.y = json_dict['y'];
	this.unitType = UnitType.fromString(json_dict['unitType']);
	this.player = json_dict['player'];
	this.health = json_dict['health'];
	this.moves = json_dict['moves'];

	// strength
    this.meleeStrength = json_dict['meleeStrength'];
    this.rangedStrength = json_dict['rangedStrength'];
    this.rangedRange = json_dict['rangedRange'];

	console.log('Unit ' + this.location.x + ', ' + this.location.y + ' => ' + this.unitType);
}

Unit.prototype.icon = function() {
    return '/static/smarthexboard/img/units/' + this.unitType.texture;
}

Unit.prototype.template = function() {
    return '/static/smarthexboard/img/unit_types/' + this.unitType.template;
}

Unit.prototype.toString = function() {
    return "Unit(" + this.name + ", at: " + this.location + ", of: " + this.player + ", at: " + this.health + ")";
}

export { Unit, UnitTypes, UnitType };
