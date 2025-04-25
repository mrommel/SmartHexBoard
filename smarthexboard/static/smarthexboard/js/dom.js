/**
 * DOM generic functions
 *
 * Copyright (c) 2020 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

// can be called with an id string or an element object directly
// return a pointer to the newly created tag
function addTag(parent, tag) {
	let e;
	const t = document.createElement(tag);

	if (typeof(parent) === 'string') {
	    e = document.getElementById(parent);
	} else {
	    e = parent;
	}

	if (e !== null) {
		e.appendChild(t);
	}

	return t;
}

function isVisible(tag) {
	const v = document.getElementById(tag).style.display;
	return v !== "" && v !== "none";
}

function makeVisible(tag) {
	document.getElementById(tag).style.display = "block";
	document.getElementById(tag).focus();
}

function makeHidden(tag) {
	document.getElementById(tag).style.display = "none";
	document.getElementById('game').focus() // focus back the game canvas
}