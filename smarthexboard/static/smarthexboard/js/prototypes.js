/**
 * Prototypes - Generic data structures
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

function ScreenPos(x, y) {
	this.x = x;
	this.y = y;
}

function Cell(row, col) {
	this.row = row;
	this.col = col;
}

function MouseInfo(x, y, right_click) {
	this.x = x;
	this.y = y;
	this.right_click = right_click;
}