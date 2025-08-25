import { HexCube, HexPoint } from "./base/point.js";
import {BuildingTypes, DistrictTypes, EraType, EraTypes, TechTypes, Yields} from "./game/types.js";

function Tester() {
    this.tests = {
        'HexPoint.constructor': test_HexPoint_constructor,
        'HexPoint.fromHexCube': test_HexPoint_fromHexCube,
        'HexCube.constructor': test_HexCube_constructor,
        'HexCube.fromHexPoint': test_HexCube_fromHexPoint,
        'HexCube.distanceTo': test_HexCube_distanceTo,
        'Yields.constructor': test_Yields_constructor,
        'Yields.addValue': test_Yields_addValue,
        'EraTypes.length': test_EraTypes_length,
        'EraType.constructor': test_EraType_constructor,
        'EraType.fromString': test_EraType_fromString,
        'TechTypes.length': test_TechTypes_length,
        'TechType.constructor': test_TechType_constructor,
        'TechType.required': test_TechType_required,
        'TechType.leadsTo': test_TechType_leadsTo,
        'DistrictTypes.length': test_DistrictTypes_length,
        'DistrictType.constructor': test_DistrictType_constructor,
        'BuildingTypes.length': test_BuildingTypes_length,
        'BuildingType.constructor': test_BuildingType_constructor
    }
}

Tester.prototype.runTests = function(callback) {
    console.log('starting tests...');
    for (const [test_name, test_method] of Object.entries(this.tests)) {
        try {
            console.log('running ' + test_name + '...');
            test_method();
            console.log(test_name + ' passed.');
            callback(true, test_name, 'passed');
        } catch (error) {
            console.error(test_name + ' failed: ' + error.message);
            callback(false, test_name, 'failed: ' + error.message);
        }
    }
    console.log('finished testing...');
}

function expect(received){
    return {
        toBe: (expected) => {
            if (received !== expected) {
                throw new Error(`Expected ${expected} but received ${received}.`);
            }
            return true;
        }
    }
}

function test_HexPoint_constructor() {
    const pt0 = new HexPoint();
    expect(pt0.x).toBe(0);
    expect(pt0.y).toBe(0);

    const pt1 = new HexPoint(1, 1);
    expect(pt1.x).toBe(1);
    expect(pt1.y).toBe(1);
}

function test_HexPoint_fromHexCube() {
    const pt = new HexPoint(1, 1);
    const cb = new HexCube(0, 0, 0);
    pt.fromHexCube(cb);

    expect(pt.x).toBe(0);
    expect(pt.y).toBe(0);
}

function test_HexCube_constructor() {
    const cb = new HexCube(1, 1, 4);

    expect(cb.q).toBe(1);
    expect(cb.r).toBe(1);
    expect(cb.s).toBe(4);
}

function test_HexCube_fromHexPoint() {
    const pt = new HexPoint(1, 1);
    const cb = new HexCube(pt);

    expect(cb.q).toBe(0);
    expect(cb.r).toBe(-1);
    expect(cb.s).toBe(1);
}

function test_HexCube_distanceTo() {
    const cb1 = new HexCube(0, 0, 0);
    const cb2 = new HexCube(1, 1, 1);
    const dist = cb1.distanceTo(cb2);

    expect(dist).toBe(1);
}

function test_Yields_constructor() {
    const y = new Yields(1, 2, 3, 4, 5, 6, 7);

    expect(y.food).toBe(1);
    expect(y.production).toBe(2);
    expect(y.gold).toBe(3);
    expect(y.science).toBe(4);
    expect(y.culture).toBe(5);
    expect(y.faith).toBe(6);
    expect(y.tourism).toBe(7);
}

function test_Yields_addValue() {
    const y = new Yields(1, 2, 3, 4, 5, 6, 7);

    y.addValue('food', 2);
    expect(y.food).toBe(3);
    y.addValue('production', 3);
    expect(y.production).toBe(5);
    y.addValue('gold', 4);
    expect(y.gold).toBe(7);
    y.addValue('science', 5);
    expect(y.science).toBe(9);
    y.addValue('culture', 6);
    expect(y.culture).toBe(11);
    y.addValue('faith', 7);
    expect(y.faith).toBe(13);
    y.addValue('tourism', 8);
    expect(y.tourism).toBe(15);
}

function test_EraTypes_length() {
    expect(Object.keys(EraTypes).length).toBe(10);
}

function test_EraType_constructor() {
    const ancient = EraTypes.ancient;

    expect(ancient.name).toBe('ancient');
}

function test_EraType_fromString() {
    const actual = EraType.fromString('classical');
    expect(actual).toBe(EraTypes.classical);
}

function test_TechTypes_length() {
    expect(Object.keys(TechTypes).length).toBe(12);
}

function test_TechType_constructor() {
    const animalHusbandry = TechTypes.animalHusbandry;

    expect(animalHusbandry.name).toBe('animalHusbandry');
    expect(animalHusbandry.eraValue).toBe(EraTypes.ancient);
    expect(animalHusbandry.texture).toBe('tech-animalHusbandry@3x.png');
    expect(animalHusbandry.costValue).toBe(25);
    expect(animalHusbandry.requiredTechs.length).toBe(0);
}

function test_TechType_required() {
    const archery = TechTypes.archery;
    const requiredTechs = archery.required();

    expect(requiredTechs.length).toBe(1);
    expect(requiredTechs[0]).toBe(TechTypes.animalHusbandry);
}

function test_TechType_leadsTo() {
    const animalHusbandry = TechTypes.animalHusbandry;
    const leadsToTechs = animalHusbandry.leadsTo();

    expect(leadsToTechs.length).toBe(1);
    expect(leadsToTechs[0]).toBe(TechTypes.archery);
}

function test_DistrictTypes_length() {
    expect(Object.keys(DistrictTypes).length).toBe(2);
}

function test_DistrictType_constructor() {
    const cityCenter = DistrictTypes.cityCenter;

    expect(cityCenter.name).toBe('cityCenter');
    expect(cityCenter.icon).toBe('district-cityCenter@3x.png');
}

function test_BuildingTypes_length() {
    expect(Object.keys(BuildingTypes).length).toBe(2);
}

function test_BuildingType_constructor() {
    const monument = BuildingTypes.monument;

    expect(monument.name).toBe('monument');
    expect(monument.icon).toBe('building-monument@3x.png');
}

export {
    Tester
};