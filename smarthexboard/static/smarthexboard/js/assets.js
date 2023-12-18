/**
 * Assets - pre-loads static assets
 *
 * Copyright (c) 2023 MiRo
 * Licensed under the GPL license:
 * http://www.gnu.org/licenses/gpl.html
 */

import { TerrainTypes, BeachTypes, SnowTypes, FeatureTypes, ResourceTypes } from './map/types.js';
import { UnitTypes } from './map/unit.js';
import { TechTypes } from './game/types.js';

function Assets() {

    // tile image cache dicts
	this.imgTerrains = {};
	this.imgResources = {};
	this.imgFeatures = {};

	// game image cache dicts
	this.imgTechs = {};
	this.imgUnits = {};

	this.tileTexturesLoaded = false;
	this.gameTexturesLoaded = false;
}

Assets.prototype.cacheTileImages = function(callbackFunction) {

    var imgList = [];

	Object.values(TerrainTypes).forEach(terrainType => {
	    terrainType.textures.forEach(terrainTexture => {
	        imgList.push(terrainTexture);
	    });
	    terrainType.hillsTextures.forEach(terrainTexture => {
	        imgList.push(terrainTexture);
	    });
	});
	Object.values(SnowTypes).forEach(snowType => {
	    imgList.push(snowType.textures[0]);
	});
	Object.values(BeachTypes).forEach(beachType => {
	    imgList.push(beachType.textures[0]);
	});
	Object.values(FeatureTypes).forEach(featureType => {
	    featureType.textures.forEach(featureTexture => {
	        imgList.push(featureTexture);
	    });
	});
	Object.values(ResourceTypes).forEach(resourceType => {
	    imgList.push(resourceType.texture);
	});

	var loaded = 0;
	var failed = 0;
    var toLoad = Object.keys(imgList).length;
    var _this = this;

    console.log('start caching ' + toLoad + ' images');

    for (var i in imgList) {
        var imgName = imgList[i];

        if (imgName.startsWith('terrain_')) {
            if (typeof this.imgTerrains[imgName] !== "undefined") {
                loaded++;
                continue;
            }

            this.imgTerrains[imgName] = new Image();
            this.imgTerrains[imgName].onload = function() {
                loaded++;
                if ((loaded + failed) == toLoad) {
                    _this.tileTexturesLoaded = true;
                    if (callbackFunction) {
                        callbackFunction();
                    }
                }
            }
            this.imgTerrains[imgName].onerror = function() {
                failed++;
                console.log('Failed to load ' + this.src + ' terrain asset');
            }
            this.imgTerrains[imgName].src = '/static/smarthexboard/img/terrains/' + imgName;

        } else if (imgName.startsWith('beach-')) {
            if (typeof this.imgTerrains[imgName] !== "undefined") {
                loaded++;
                continue;
            }

            this.imgTerrains[imgName] = new Image();
            this.imgTerrains[imgName].onload = function() {
                loaded++;
                if ((loaded + failed) == toLoad) {
                    _this.tileTexturesLoaded = true;
                    if (callbackFunction) {
                        callbackFunction();
                    }
                }
            }
            this.imgTerrains[imgName].onerror = function() {
                failed++;
                console.log('Failed to load ' + this.src + ' beach asset');
            }
            this.imgTerrains[imgName].src = '/static/smarthexboard/img/beaches/' + imgName;

        } else if (imgName.startsWith('snow-')) {
            if (typeof this.imgTerrains[imgName] !== "undefined") {
                loaded++;
                continue;
            }

            this.imgTerrains[imgName] = new Image();
            this.imgTerrains[imgName].onload = function() {
                loaded++;
                if ((loaded + failed) == toLoad) {
                    _this.tileTexturesLoaded = true;
                    if (callbackFunction) {
                        callbackFunction();
                    }
                }
            }
            this.imgTerrains[imgName].onerror = function() {
                failed++;
                console.log('Failed to load ' + this.src + ' snow asset');
            }
            this.imgTerrains[imgName].src = '/static/smarthexboard/img/snow/' + imgName;

        } else if (imgName.startsWith('feature_')) {
            if (typeof this.imgFeatures[imgName] !== "undefined") {
                loaded++;
                continue;
            }

            this.imgFeatures[imgName] = new Image();
            this.imgFeatures[imgName].onload = function() {
                loaded++;
                if ((loaded + failed) == toLoad) {
                    _this.tileTexturesLoaded = true;
                    if (callbackFunction) {
                        callbackFunction();
                    }
                }
            }
            this.imgFeatures[imgName].onerror = function() {
                failed++;
                console.log('Failed to load ' + this.src + ' feature asset');
            }
            this.imgFeatures[imgName].src = '/static/smarthexboard/img/features/' + imgName;

        } else if (imgName.startsWith('resource_')) {
            if (typeof this.imgResources[imgName] !== "undefined") {
                loaded++;
                continue;
            }

            this.imgResources[imgName] = new Image();
            this.imgResources[imgName].onload = function() {
                loaded++;
                if ((loaded + failed) == toLoad) {
                    _this.tileTexturesLoaded = true;
                    if (callbackFunction) {
                        callbackFunction();
                    }
                }
            }
            this.imgResources[imgName].onerror = function() {
                failed++;
                console.log('Failed to load ' + this.src + ' resource asset');
            }
            this.imgResources[imgName].src = '/static/smarthexboard/img/resources/' + imgName;
        } else {
            failed++;
            console.log('image type not handled: ' + imgName);
        }
    }
}

// Caches images, func a function to call upon cache completion
Assets.prototype.cacheGameImages = function(callbackFunction) {
	var imgList = [];

    Object.values(TechTypes).forEach(techType => {
	    imgList.push(techType.texture);
	});
	Object.values(UnitTypes).forEach(unitType => {
	    imgList.push(unitType.texture);
	});

	var loaded = 0;
	var failed = 0;
    var toLoad = Object.keys(imgList).length;
    var _this = this;

    console.log('start caching ' + toLoad + ' game images');

    for (var i in imgList) {
        var imgName = imgList[i];

        if (imgName.startsWith('tech-')) {
            if (typeof this.imgTechs[imgName] !== "undefined") {
                loaded++;
                continue;
            }

            this.imgTechs[imgName] = new Image();
            this.imgTechs[imgName].onload = function() {
                loaded++;
                if ((loaded + failed) == toLoad) {
                    if (callbackFunction) {
                        _this.gameTexturesLoaded = true;
                        callbackFunction();
                    }
                }
            }
            this.imgTechs[imgName].onerror = function() {
                failed++;
                console.log('Failed to load ' + this.src + ' tech asset');
            }
            this.imgTechs[imgName].src = '/static/smarthexboard/img/techs/' + imgName;
        } else if (imgName.startsWith('unit-')) {
            if (typeof this.imgUnits[imgName] !== "undefined") {
                loaded++;
                continue;
            }

            this.imgUnits[imgName] = new Image();
            this.imgUnits[imgName].onload = function() {
                loaded++;
                if ((loaded + failed) == toLoad) {
                    if (callbackFunction) {
                        _this.gameTexturesLoaded = true;
                        callbackFunction();
                    }
                }
            }
            this.imgUnits[imgName].onerror = function() {
                failed++;
                console.log('Failed to load ' + this.src + ' unit asset');
            }
            this.imgUnits[imgName].src = '/static/smarthexboard/img/units/' + imgName;
        } else {
            failed++;
            console.log('image type not handled: ' + imgName);
        }
    }
}

/*Assets.prototype.cleanupTileImagesCache = function(imgList) {
    for (var i in imgTerrains) {
        if (typeof imgList[imgUnits[i]] !== "undefined") {
            // console.log("Removing unused entry %s", imgUnits[i].src);
            imgTerrains[i] = null;
            delete(imgTerrains[i]);
        }
    }
}*/

Assets.prototype.terrainTexture = function(textureName) {

    if (!this.tileTexturesLoaded) {
        console.log('Try to get terrain texture: ' + textureName + ' but cache is not initialized.');
        return new Image();
    }

    if (!this.imgTerrains.hasOwnProperty(textureName)) {
        console.log('Try to get terrain texture: ' + textureName + ' but is not in cache.');
        return new Image();
    }

    return this.imgTerrains[textureName];
}

Assets.prototype.coastTexture = function(textureName) {

    if (!this.tileTexturesLoaded) {
        console.log('Try to get coast texture: ' + textureName + ' but cache is not initialized.');
        return new Image();
    }

    if (!this.imgTerrains.hasOwnProperty(textureName)) {
        console.log('Try to get coast texture: ' + textureName + ' but is not in cache.');
        return new Image();
    }

    return this.imgTerrains[textureName];
}

Assets.prototype.featureTexture = function(textureName) {

    if (!this.tileTexturesLoaded) {
        console.log('Try to get feature texture: ' + textureName + ' but cache is not initialized.');
        return new Image();
    }

    if (!this.imgFeatures.hasOwnProperty(textureName)) {
        console.log('Try to get feature texture: ' + textureName + ' but is not in cache.');
        return new Image();
    }

    return this.imgFeatures[textureName];
}

Assets.prototype.resourceTexture = function(textureName) {

    if (!this.tileTexturesLoaded) {
        console.log('Try to get resource texture: ' + textureName + ' but cache is not initialized.');
        return new Image();
    }

    if (!this.imgResources.hasOwnProperty(textureName)) {
        console.log('Try to get resource texture: ' + textureName + ' but is not in cache.');
        return new Image();
    }

    return this.imgResources[textureName];
}

Assets.prototype.unitTexture = function(textureName) {

    if (!this.gameTexturesLoaded) {
        console.log('Try to get unit texture: ' + textureName + ' but cache is not initialized.');
        return new Image();
    }

    if (!this.imgUnits.hasOwnProperty(textureName)) {
        console.log('Try to get unit texture: ' + textureName + ' but is not in cache.');
        return new Image();
    }

    return this.imgUnits[textureName];
}

export { Assets };