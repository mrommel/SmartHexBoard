import { HexCube, HexPoint } from "./base/point.js";
import {Yields} from "./game/types.js";

function Tester() {
    this.tests = {
        'HexPoint.constructor': test1_HexPoint_constructor,
        'HexPoint.fromHexCube': test2_HexPoint_fromHexCube,
        'HexCube.constructor': test3_HexCube_constructor,
        'HexCube.fromHexPoint': test4_HexCube_fromHexPoint,
        'HexCube.distanceTo': test5_HexCube_distanceTo,
        'Yields.addValue': test6_Yields_addValue
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

function test1_HexPoint_constructor() {
    const pt0 = new HexPoint();
    expect(pt0.x).toBe(0);
    expect(pt0.y).toBe(0);

    const pt1 = new HexPoint(1, 1);
    expect(pt1.x).toBe(1);
    expect(pt1.y).toBe(1);
}

function test2_HexPoint_fromHexCube() {
    const pt = new HexPoint(1, 1);
    const cb = new HexCube(0, 0, 0);
    pt.fromHexCube(cb);

    expect(pt.x).toBe(0);
    expect(pt.y).toBe(0);
}

function test3_HexCube_constructor() {
    const cb = new HexCube(1, 1, 4);

    expect(cb.q).toBe(1);
    expect(cb.r).toBe(1);
    expect(cb.s).toBe(4);
}

function test4_HexCube_fromHexPoint() {
    const pt = new HexPoint(1, 1);
    const cb = new HexCube(pt);

    expect(cb.q).toBe(0);
    expect(cb.r).toBe(-1);
    expect(cb.s).toBe(1);
}

function test5_HexCube_distanceTo() {
    const cb1 = new HexCube(0, 0, 0);
    const cb2 = new HexCube(1, 1, 1);
    const dist = cb1.distanceTo(cb2);

    expect(dist).toBe(1);
}

function test6_Yields_addValue() {
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

export {
    Tester
};