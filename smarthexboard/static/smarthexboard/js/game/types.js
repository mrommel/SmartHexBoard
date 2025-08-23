/**
 * Game - Provides basic game objects
 *
 * Copyright (c) 2023 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

// EraType Constructor

function EraType(name) {
    this.name = name;
}

EraType.prototype.clone = function() {
    return new TechType(this.name);
}

EraType.prototype.toString = function() {
    return '[EraType: ' + this.name + ']';
}

EraType.fromString = function(era_identifier) {

    switch (era_identifier) {
        case 'none':
            return EraTypes.none.clone();

        case 'ancient':
            return EraTypes.ancient.clone();
        case 'classical':
            return EraTypes.classical.clone();
        case 'medieval':
            return EraTypes.medieval.clone();
        case 'renaissance':
            return EraTypes.renaissance.clone();
        case 'industrial':
            return EraTypes.industrial.clone();
        case 'modern':
            return EraTypes.modern.clone();
        case 'atomic':
            return EraTypes.atomic.clone();
        case 'information':
            return EraTypes.information.clone();
        case 'future':
            return EraTypes.future.clone();

        default:
            throw Error('Unsupported era identifier: ' + tech_identifier);
    }
}

var EraTypes = {
	none: new EraType("none"),
	ancient: new EraType("ancient"),
	classical: new EraType("classical"),
	medieval: new EraType("medieval"),
	renaissance: new EraType("renaissance"),
	industrial: new EraType("industrial"),
	modern: new EraType("modern"),
	atomic: new EraType("atomic"),
	information: new EraType("information"),
	future: new EraType("future"),
};

// TechType Constructor

function TechType(name, era, cost, requiredTechs, texture) {
    this.name = name;
    this.eraValue = era;
    this.costValue = cost;
    this.requiredTechs = requiredTechs;
    this.texture = texture;
}

TechType.prototype.era = function() {
    return this.eraValue
}

TechType.prototype.cost = function() {
    return this.costValue;
}

TechType.prototype.required = function() {
    var techs = [];
    this.requiredTechs.forEach(tech_name => {
        techs.append(TechType.fromString(tech_name));
    });
    return techs;
}

TechType.prototype.leadsTo = function() {
    var leadingTo = []

    Object.values(TechTypes).forEach(techType => {
        if (tech.required().contains(this)) {
            leadingTo.append(tech)
        }
    });

    return leadingTo
}

TechType.prototype.clone = function() {
    return new TechType(this.name, this.eraValue, this.costValue, this.requiredTechs, this.texture);
}

TechType.prototype.toString = function() {
    return '[TechType: ' + this.name + ']';
}

TechType.fromString = function(tech_identifier) {

    switch (tech_identifier) {
        case 'none':
            return TechTypes.none.clone();

            // ancient
        case 'mining':
            return TechTypes.mining.clone();
        case 'pottery':
            return TechTypes.pottery.clone();
        case 'animalHusbandry':
            return TechTypes.animalHusbandry.clone();
        case 'sailing':
            return TechTypes.sailing.clone();
        case 'astrology':
            return TechTypes.astrology.clone();
        case 'irrigation':
            return TechTypes.irrigation.clone();
        case 'writing':
            return TechTypes.writing.clone();
        case 'masonry':
            return TechTypes.masonry.clone();
        case 'archery':
            return TechTypes.archery.clone();
        case 'bronzeWorking':
            return TechTypes.bronzeWorking.clone();
        case 'wheel':
            return TechTypes.wheel.clone();

            // classical

        default:
            throw Error('Unsupported tech identifier: ' + tech_identifier);
    }
}

var TechTypes = {
        // default
	none: new TechType("none", EraTypes.ancient.clone(), -1, [], "tech-pottery@3x.png"),

	    // ancient
	mining: new TechType("mining", EraTypes.ancient.clone(), 25, [], "tech-mining@3x.png"),
	pottery: new TechType("pottery", EraTypes.ancient.clone(), 25, [], "tech-pottery@3x.png"),
    animalHusbandry: new TechType("animalHusbandry", EraTypes.ancient.clone(), 25, [], "tech-animalHusbandry@3x.png"),
    sailing: new TechType("sailing", EraTypes.ancient.clone(), 50, [], "tech-sailing@3x.png"),
    astrology: new TechType("astrology", EraTypes.ancient.clone(), 50, [], "tech-astrology@3x.png"),
    irrigation: new TechType("irrigation", EraTypes.ancient.clone(), 50, ['pottery'], "tech-irrigation@3x.png"),
    writing: new TechType("writing", EraTypes.ancient.clone(), 50, ['pottery'], "tech-writing@3x.png"),
    masonry: new TechType("masonry", EraTypes.ancient.clone(), 80, ['mining'], "tech-masonry@3x.png"),
    archery: new TechType("archery", EraTypes.ancient.clone(), 50, ['animalHusbandry'], "tech-archery@3x.png"),
    bronzeWorking: new TechType("bronzeWorking", EraTypes.ancient.clone(), 80, ['mining'], "tech-bronzeWorking@3x.png"),
    wheel: new TechType("wheel", EraTypes.ancient.clone(), 80, ['mining'], "tech-wheel@3x.png"),

        // classical
    /*case celestialNavigation
    case horsebackRiding
    case currency
    case construction
    case ironWorking
    case shipBuilding
    case mathematics
    case engineering

        // medieval
    case militaryTactics
    case buttress
    case apprenticeship
    case stirrups
    case machinery
    case education
    case militaryEngineering
    case castles

        // renaissance
    case cartography
    case massProduction
    case banking
    case gunpowder
    case printing
    case squareRigging
    case astronomy
    case metalCasting
    case siegeTactics

        // industrial
    case industrialization
    case scientificTheory
    case ballistics
    case militaryScience
    case steamPower
    case sanitation
    case economics
    case rifling

        // modern
    case flight
    case replaceableParts
    case steel
    case refining
    case electricity
    case radio
    case chemistry
    case combustion

        // atomic
    case advancedFlight
    case rocketry
    case advancedBallistics
    case combinedArms
    case plastics
    case computers
    case nuclearFission
    case syntheticMaterials

        // information
    case telecommunications
    case satellites
    case guidanceSystems
    case lasers
    case composites
    case stealthTechnology
    case robotics
    case nuclearFusion
    case nanotechnology

        // future
    case futureTech*/
}

// YieldType Constructor

const YieldTypes = Object.freeze({
    FOOD:   Symbol("food"),
    PRODUCTION:  Symbol("production"),
    GOLD: Symbol("gold"),
    SCIENCE: Symbol("science"),
    CULTURE: Symbol("culture"),
    FAITH: Symbol("faith"),
    TOURISM: Symbol("tourism"),
});

// Yields Constructor

function Yields(food=0, production=0, gold=0, science=0, culture=0, faith=0, tourism=0) {
    this.food = food;
    this.production = production;
    this.gold = gold;
    this.science = science;
    this.culture = culture;
    this.faith = faith;
    this.tourism = tourism;
}

Yields.prototype.toString = function() {
    return '[Yields: food=' + this.food + ', production=' + this.production + ', gold=' + this.gold + ', science=' + this.science + ', culture=' + this.culture + ', faith=' + this.faith + ', tourism=' + this.tourism + ']';
}


export {
    EraType,
    EraTypes,
    TechType,
    TechTypes,
    YieldTypes,
    Yields,
};