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

// CityInfo Constructor

function CityInfo() {
    // Citizen growth
    this.food_per_turn = 0;
    this.food_consumption = 0;
    this.growth_food_per_turn = 0;
    this.amenities_growth_bonus = 0;
    this.other_growth_bonus = 0;
    this.modified_food_per_turn = 0;
    this.housing_multiplier = 0;
    this.occupied_city_multiplier = 0;
    this.total_food_surplus = 0;
    this.growth_in_turns = 0;

    // amenities
    this.amenities_present = 0;
    this.amenities_needed = 0;
    this.amenities_status = 'CONTENT';
    // ...

    // housing
    this.housing_present = 0;
    this.housing_needed = 0;
    this.housing_status = 'CONTENT';

    this.housing_from_buildings = 0;
    this.housing_from_civics = 0;
    this.housing_from_districs = 0;
    this.housing_from_improvements = 0;
    this.housing_from_wonders = 0;
    // ...

    // CityInfo
    this.buildings_and_districts = [];
    this.wonders = [];
    this.trading_posts = [];

    this.yields = {
        food: 0,
        production: 0,
        gold: 0,
        science: 0,
        culture: 0,
        faith: 0
    }
}

// Unit Object Public Methods

CityInfo.prototype.fromJson = function(json_dict) {

}

export { City, CityInfo };