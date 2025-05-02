// City Constructor

import {HexPoint} from "../base/point.js";

function City() {

    this.name = "";
    this.location = new HexPoint();
    this.player = -1;
	this.health = 0;
    this.size = 0;
}

// City Object Public Methods

City.prototype.fromJson = function(json_dict) {

    this.name = json_dict['name'];
    this.location.x = json_dict['x'];
	this.location.y = json_dict['y'];
	this.player = json_dict['player'];
	this.health = json_dict['health'];
    this.size = json_dict['size'];

	console.log('City ' + this.location.x + ', ' + this.location.y + ' => ' + this.player);
}

City.prototype.toString = function() {
    return "City(" + this.name + ", at: " + this.location + ", of: " + this.player + ", at: " + this.health + ")";
}

export { City };