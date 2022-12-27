/*================
 Template Name:
 Description: All type of data science, artificial intelligence & machine learning template.
 Version: 1.0
 Author:
=======================*/

// TABLE OF CONTENTS
// 1. preloader
// 2. canvas full screen

jQuery(function ($) {

    'use strict';

    // make canvas full screen
    $(document).ready(function () {
        test1_HexPoint_constructor();
        test2_HexPoint_fromHexCube();
        test3_HexCube_constructor();
        test4_HexCube_fromHexPoint();
        test5_HexCube_distanceTo();

        // hide pre-loader
        $('#preloader').delay(200).fadeOut('fade');
    });

}); // JQuery end

function test1_HexPoint_constructor() {
    var pt0 = new HexPoint();

    if (pt0.x == 0 && pt0.y == 0) {
        $('#tests').append('<p>Test1.0 successful</p>');
    } else {
        $('#tests').append('<p>Test1.0 failed: ' + pt0 + '</p>');
    }

    var pt1 = new HexPoint(1, 1);

    if (pt1.x == 1 && pt1.y == 1) {
        $('#tests').append('<p>Test1.1 successful</p>');
    } else {
        $('#tests').append('<p>Test1.1 failed: ' + pt1 + '</p>');
    }
}

function test2_HexPoint_fromHexCube() {
    var pt = new HexPoint(1, 1);
    var cb = new HexCube(0, 0, 0);
    pt.fromHexCube(cb);

    if (pt.x == 0 && pt.y == 0) {
        $('#tests').append('<p>Test2 successful</p>');
    } else {
        $('#tests').append('<p>Test2 failed: ' + pt + '</p>');
    }
}

function test3_HexCube_constructor() {
    var cb = new HexCube(1, 1, 4);

    if (cb.q == 1 && cb.r == 1 && cb.s == 4) {
        $('#tests').append('<p>Test2 successful</p>');
    } else {
        $('#tests').append('<p>Test2 failed: ' + cb + '</p>');
    }
}

function test4_HexCube_fromHexPoint() {
    var cb = new HexCube(0, 0, 0);
    var pt = new HexPoint(1, 1);
    cb.fromHexPoint(pt);

    if (cb.q == 0 && cb.r == -1 && cb.s == 1) {
        $('#tests').append('<p>Test3 successful</p>');
    } else {
        $('#tests').append('<p>Test3 failed: ' + cb + '</p>');
    }
}

function test5_HexCube_distanceTo() {
    var cb1 = new HexCube(0, 0, 0);
    var cb2 = new HexCube(1, 1, 1);
    var dist = cb1.distanceTo(cb2);

    if (dist === 1) {
        $('#tests').append('<p>Test4 successful</p>');
    } else {
        $('#tests').append('<p>Test4 failed: ' + dist + '</p>');
    }
}