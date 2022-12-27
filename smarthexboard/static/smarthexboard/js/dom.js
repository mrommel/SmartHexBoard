/**
 * DOM generic functions
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

// can be called with a id string or a element object directly
// return pointer to the newly created tag
function addTag(parent, tag) {
	var e;
	var t = document.createElement(tag);

	if (typeof(parent) === 'string') {	e = document.getElementById(parent); }
	else {e = parent;}

	if (e !== null)
		e.appendChild(t);

	return t;
}

function isVisible(tag) {
	var v = document.getElementById(tag).style.display;

	if (v != "" && v != "none")
		return true;

	return false;
}

function makeVisible(tag) {
	document.getElementById(tag).style.display = "inline";
	document.getElementById(tag).focus();
}

function makeHidden(tag) {
	document.getElementById(tag).style.display = "none";
	document.getElementById('game').focus() //focus back the game canvas
}