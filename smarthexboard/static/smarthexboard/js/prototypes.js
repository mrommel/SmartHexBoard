/**
 * Prototypes - Generic data structures
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

function CGSize(width, height) {
    this.width = width;
    this.height = height;
}

function CGPoint(x, y) {
    this.x = x;
    this.y = y;
}

function MouseInfo(x, y, right_click) {
	this.x = x;
	this.y = y;
	this.right_click = right_click;
}