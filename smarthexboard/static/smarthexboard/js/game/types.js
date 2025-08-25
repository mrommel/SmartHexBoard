/**
 * Game - Provides basic game objects
 *
 * Copyright (c) 2023 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

// EraType Constructor

/**
 * constructor of an EraType
 * @param {String} name - name of the era
 * @constructor
 */
function EraType(name) {
    this.name = name;
}

/**
 * Function to get a string representation for this EraType
 * @returns {String}
 */
EraType.prototype.toString = function() {
    return '[EraType: ' + this.name + ']';
}

/**
 * Function to get an EraType from a string identifier
 * @param {String} era_identifier - string identifier of the EraType
 * @returns {EraType}
 */
EraType.fromString = function(era_identifier) {

    switch (era_identifier) {
        case 'none':
            return EraTypes.none;

        case 'ancient':
            return EraTypes.ancient;
        case 'classical':
            return EraTypes.classical;
        case 'medieval':
            return EraTypes.medieval;
        case 'renaissance':
            return EraTypes.renaissance;
        case 'industrial':
            return EraTypes.industrial;
        case 'modern':
            return EraTypes.modern;
        case 'atomic':
            return EraTypes.atomic;
        case 'information':
            return EraTypes.information;
        case 'future':
            return EraTypes.future;

        default:
            throw Error('Unsupported era identifier: ' + era_identifier);
    }
}

/**
 * All EraTypes in the game
 */
const EraTypes = {
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

/**
 * constructor of a TechType
 * @param {String} name - name of the technology
 * @param {EraType} era - era of the technology
 * @param {Number} cost - science cost to acquire this technology
 * @param {Array} requiredTechs - array of string identifiers of required TechTypes
 * @param {String} texture - icon texture for this technology
 * @constructor
 */
function TechType(name, era, cost, requiredTechs, texture) {
    this.name = name;
    this.eraValue = era;
    this.costValue = cost;
    this.requiredTechs = requiredTechs;
    this.texture = texture;
}

/**
 * Function to get the EraType of this TechType
 * @returns {EraType}
 */
TechType.prototype.era = function() {
    return this.eraValue
}

/**
 * Function to get the science cost to acquire this TechType
 * @returns {Number}
 */
TechType.prototype.cost = function() {
    return this.costValue;
}

/**
 * Function to get all TechTypes required for this TechType
 * @returns {Array}
 */
TechType.prototype.required = function() {
    const techs = [];

    this.requiredTechs.forEach(tech_name => {
        techs.push(TechType.fromString(tech_name));
    });

    return techs;
}

/**
 * Function to get all TechTypes that require this TechType
 * @returns {Array}
 */
TechType.prototype.leadsTo = function() {
    const leadingTo = [];

    Object.values(TechTypes).forEach(techType => {
        if (techType.required().indexOf(this) !== -1) {
            leadingTo.push(techType)
        }
    });

    return leadingTo
}

/**
 * Function to get a string representation for this TechType
 * @returns {String}
 */
TechType.prototype.toString = function() {
    return '[TechType: ' + this.name + ']';
}

/**
 * Function to get a TechType from a string identifier
 * @param {String} tech_identifier - string identifier of the TechType
 * @returns {TechType}
 */
TechType.fromString = function(tech_identifier) {

    switch (tech_identifier) {
        case 'none':
            return TechTypes.none;

            // ancient
        case 'mining':
            return TechTypes.mining;
        case 'pottery':
            return TechTypes.pottery;
        case 'animalHusbandry':
            return TechTypes.animalHusbandry;
        case 'sailing':
            return TechTypes.sailing;
        case 'astrology':
            return TechTypes.astrology;
        case 'irrigation':
            return TechTypes.irrigation;
        case 'writing':
            return TechTypes.writing;
        case 'masonry':
            return TechTypes.masonry;
        case 'archery':
            return TechTypes.archery;
        case 'bronzeWorking':
            return TechTypes.bronzeWorking;
        case 'wheel':
            return TechTypes.wheel;

            // classical

        default:
            throw Error('Unsupported tech identifier: ' + tech_identifier);
    }
}

/**
 * All TechTypes in the game
 */
const TechTypes = {
        // default
	none: new TechType("none", EraTypes.ancient, -1, [], "tech-pottery@3x.png"),

	    // ancient
	mining: new TechType("mining", EraTypes.ancient, 25, [], "tech-mining@3x.png"),
	pottery: new TechType("pottery", EraTypes.ancient, 25, [], "tech-pottery@3x.png"),
    animalHusbandry: new TechType("animalHusbandry", EraTypes.ancient, 25, [], "tech-animalHusbandry@3x.png"),
    sailing: new TechType("sailing", EraTypes.ancient, 50, [], "tech-sailing@3x.png"),
    astrology: new TechType("astrology", EraTypes.ancient, 50, [], "tech-astrology@3x.png"),
    irrigation: new TechType("irrigation", EraTypes.ancient, 50, ['pottery'], "tech-irrigation@3x.png"),
    writing: new TechType("writing", EraTypes.ancient, 50, ['pottery'], "tech-writing@3x.png"),
    masonry: new TechType("masonry", EraTypes.ancient, 80, ['mining'], "tech-masonry@3x.png"),
    archery: new TechType("archery", EraTypes.ancient, 50, ['animalHusbandry'], "tech-archery@3x.png"),
    bronzeWorking: new TechType("bronzeWorking", EraTypes.ancient, 80, ['mining'], "tech-bronzeWorking@3x.png"),
    wheel: new TechType("wheel", EraTypes.ancient, 80, ['mining'], "tech-wheel@3x.png"),

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

/**
 * Constructor of a YieldType
 * @param {String} name - name of the yield type
 * @constructor
 */
function YieldType(name) {
    this.name = name;
}

/**
 * Function to get a string representation for this YieldType
 * @returns {string}
 */
YieldType.prototype.toString = function() {
    return '[YieldType: ' + this.name + ']';
}


/**
 * Enumeration of all YieldTypes in the game
 */
const YieldTypes = Object.freeze({
    FOOD: new YieldType("food"),
    PRODUCTION: new YieldType("production"),
    GOLD: new YieldType("gold"),
    SCIENCE: new YieldType("science"),
    CULTURE: new YieldType("culture"),
    FAITH: new YieldType("faith"),
    TOURISM: new YieldType("tourism"),
});

// Yields Constructor

/**
 * Constructor of a Yields object
 * @param {Number} food - amount of food
 * @param {Number} production - amount of production
 * @param {Number} gold - amount of gold
 * @param {Number} science - amount of science
 * @param {Number} culture - amount of culture
 * @param {Number} faith - amount of faith
 * @param {Number} tourism - amount of tourism
 * @constructor
 */
function Yields(food=0, production=0, gold=0, science=0, culture=0, faith=0, tourism=0) {
    this.food = food;
    this.production = production;
    this.gold = gold;
    this.science = science;
    this.culture = culture;
    this.faith = faith;
    this.tourism = tourism;
}

/**
 * Add a value to a specific yield type
 * @param {String,YieldType} yieldType - type of yield
 * @param value
 */
Yields.prototype.addValue = function(yieldType, value) {
    switch (yieldType) {
        case YieldTypes.FOOD:
        case 'food':
            this.food += value;
            break;
        case YieldTypes.PRODUCTION:
        case 'production':
            this.production += value;
            break;
        case YieldTypes.GOLD:
        case 'gold':
            this.gold += value;
            break;
        case YieldTypes.SCIENCE:
        case 'science':
            this.science += value;
            break;
        case YieldTypes.CULTURE:
        case 'culture':
            this.culture += value;
            break;
        case YieldTypes.FAITH:
        case 'faith':
            this.faith += value;
            break;
        case YieldTypes.TOURISM:
        case 'tourism':
            this.tourism += value;
            break;
        default:
            throw Error('Unsupported yield type: ' + yieldType.toString());
    }
}

/**
 * Function to get a string representation for this Yields object
 * @returns {string}
 */
Yields.prototype.toString = function() {
    let str = '[Yields: ';
    if (this.food > 0) {
        str += 'food=' + this.food + ', ';
    }
    if (this.production > 0) {
        str += 'production=' + this.production + ', ';
    }
    if (this.gold > 0) {
        str += 'gold=' + this.gold + ', ';
    }
    if (this.science > 0) {
        str += 'science=' + this.science + ', ';
    }
    if (this.culture > 0) {
        str += 'culture=' + this.culture + ', ';
    }
    if (this.faith > 0) {
        str += 'faith=' + this.faith + ', ';
    }
    if (this.tourism > 0) {
        str += 'tourism=' + this.tourism + ', ';
    }
    if (str.endsWith(', ')) {
        str = str.slice(0, -2);
    }
    str += ']';
    return str;
}

// DistrictType Constructor

/**
 * Constructor of a DistrictType
 * @param {String} name - name of the district type
 * @param {String} icon - icon texture for this district type
 * @constructor
 */
class DistrictType {
    constructor(name, icon) {
        this.name = name;
        this.icon = icon;
    }
}

/**
 * Enumeration of all DistrictTypes in the game
 */
const DistrictTypes = {
    // default
    none: new DistrictType("none", ""),

    cityCenter: new DistrictType("cityCenter", 'district-cityCenter@3x.png'),
};

// BuildingType Constructor

/**
 * Constructor of a BuildingType
 * @param {String} name - name of the building type
 * @param {String} icon - icon texture for this building type
 * @constructor
 */
class BuildingType {
    constructor(name, icon) {
        this.name = name;
        this.icon = icon;
    }
}

/**
 * Enumeration of all BuildingTypes in the game
 */
const BuildingTypes = {
    // default
    none: new BuildingType("none", "building-none@3x.png"),

    monument: new BuildingType("monument", "building-monument@3x.png"),
};


export {
    EraType,
    EraTypes,
    TechType,
    TechTypes,
    YieldTypes,
    Yields,
    DistrictType,
    DistrictTypes,
    BuildingType,
    BuildingTypes,
};