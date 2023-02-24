from enum import Enum

from smarthexboard.game.types import TechType
from smarthexboard.map.base import Size, ExtendedEnum


class MapAge(Enum):
    young = 'young'
    normal = 'normal'
    old = 'old'


class Yields:
    def __init__(self, food, production, gold, science=0, culture=0, faith=0):
        self.food = food
        self.production = production
        self.gold = gold
        self.science = science
        self.culture = culture
        self.faith = faith


class TerrainType(ExtendedEnum):
    desert = 'desert'
    grass = 'grass'
    ocean = 'ocean'
    plains = 'plains'
    shore = 'shore'
    snow = 'snow'
    tundra = 'tundra'

    land = 'land'
    sea = 'sea'

    def isWater(self):
        return self == TerrainType.sea or self == TerrainType.ocean or self == TerrainType.shore

    def isLand(self):
        return not self.isWater()

    def movementCost(self, movement_type):
        if movement_type == MovementType.immobile:
            return MovementType.max

        if movement_type == MovementType.swim:
            if self == TerrainType.ocean:
                return 1.5

            if self == TerrainType.shore:
                return 1.0

            return MovementType.max

        if movement_type == MovementType.swimShallow:
            if self == TerrainType.shore:
                return 1.0

            return MovementType.max

        if movement_type == MovementType.walk:
            if self == TerrainType.plains:
                return 1.0

            if self == TerrainType.grass:
                return 1.0

            if self == TerrainType.desert:
                return 1.0

            if self == TerrainType.tundra:
                return 1.0

            if self == TerrainType.snow:
                return 1.0

            return MovementType.max

    def textures(self):
        if self == TerrainType.desert:
            return ['terrain_desert@3x.png']

        if self == TerrainType.grass:
            return ['terrain_grass@3x.png']

        if self == TerrainType.ocean:
            return ['terrain_ocean@3x.png']

        if self == TerrainType.plains:
            return ['terrain_plains@3x.png']

        if self == TerrainType.shore:
            return ['terrain_shore@3x.png']

        if self == TerrainType.snow:
            return ['terrain_snow@3x.png']

        if self == TerrainType.tundra:
            return ['terrain_tundra@3x.png', 'terrain_tundra2@3x.png', 'terrain_tundra3@3x.png']

        return []


class FeatureData:
    def __init__(self, name, yields, is_wonder):
        self.name = name
        self.yields = yields
        self.is_wonder = is_wonder


class FeatureType(ExtendedEnum):
    none = 'none'
    atoll = 'atoll'
    fallout = 'fallout'
    floodplains = 'floodplains'
    forest = 'forest'
    ice = 'ice'
    marsh = 'marsh'
    mountains = 'mountains'
    oasis = 'oasis'
    pine = 'pine'  # special case for pine forest
    rainforest = 'rainforest'
    reef = 'reef'
    lake = 'lake'
    volcano = 'volcano'

    # natural wonder
    mountEverest = 'mountEverest'
    mountKilimanjaro = 'mountEverest'

    def data(self):
        if self == FeatureType.none:
            return FeatureData('None', Yields(0, 0, 0), False)
        if self == FeatureType.forest:
            return FeatureData('Forest', Yields(0, 1, 0), False)
        elif self == FeatureType.rainforest:
            return FeatureData('Rainforest', Yields(1, 0, 0), False)
        elif self == FeatureType.floodplains:
            return FeatureData('Floodplains', Yields(3, 0, 0), False)
        elif self == FeatureType.marsh:
            return FeatureData('Marsh', Yields(3, 0, 0), False)
        elif self == FeatureType.oasis:
            return FeatureData("Oasis", Yields(1, 0, 0), False)
        elif self == FeatureType.reef:
            return FeatureData("Reef", Yields(1, 0, 0), False)
        elif self == FeatureType.ice:
            return FeatureData("Ice", Yields(0, 0, 0), False)
        elif self == FeatureType.atoll:
            return FeatureData("Atoll", Yields(1, 0, 0), False)
        elif self == FeatureType.volcano:
            return FeatureData("Volcano", Yields(0, 0, 0), False)
        elif self == FeatureType.mountains:
            return FeatureData("Mountains", Yields(0, 0, 0), False)
        elif self == FeatureType.lake:
            return FeatureData("Lake", Yields(0, 0, 0), False)
        elif self == FeatureType.fallout:
            return FeatureData("Fallout", Yields(-3, -3, -3), False)

        raise AttributeError(f'FeatureType.data: {self} not handled!')
        # return FeatureData('None', Yields(0, 0, 0), False)

    def movementCost(self, movement_type):
        if movement_type == MovementType.immobile:
            return MovementType.max

        if movement_type == MovementType.swim:
            return MovementType.max  # this means that no unit can enter water features

        if movement_type == MovementType.swimShallow:
            return self.movementCosts()

        if movement_type == MovementType.walk:
            return self.movementCosts()

    def movementCosts(self):
        if self == FeatureType.forest:
            return 2
        elif self == FeatureType.rainforest:
            return 2
        elif self == FeatureType.floodplains:
            return 0
        elif self == FeatureType.marsh:
            return 2
        elif self == FeatureType.oasis:
            return 0
        elif self == FeatureType.reef:
            return 2
        elif self == FeatureType.ice:
            return MovementType.max
        elif self == FeatureType.atoll:
            return 2
        elif self == FeatureType.volcano:
            return MovementType.max
        elif self == FeatureType.mountains:
            return 2  # ???
        elif self == FeatureType.lake:
            return MovementType.max
        elif self == FeatureType.fallout:
            return 2

        return MovementType.max

    def isPossibleOn(self, tile):
        if self == FeatureType.forest:
            return self._isForestPossibleOn(tile)
        elif self == FeatureType.rainforest:
            return self._isRainforestPossibleOn(tile)
        elif self == FeatureType.floodplains:
            return self._isFloodplainsPossibleOn(tile)
        elif self == FeatureType.marsh:
            return self._isMarshPossibleOn(tile)
        elif self == FeatureType.oasis:
            return self._isOasisPossibleOn(tile)
        elif self == FeatureType.reef:
            return self._isReefPossibleOn(tile)
        elif self == FeatureType.ice:
            return self._isIcePossibleOn(tile)
        elif self == FeatureType.atoll:
            return self._isAtollPossibleOn(tile)
        elif self == FeatureType.volcano:
            return self._isVolcanoPossibleOn(tile)
        #
        elif self == FeatureType.mountains:
            return self._isMountainPossibleOn(tile)
        elif self == FeatureType.lake:
            return self._isLakePossibleOn(tile)
        elif self == FeatureType.fallout:
            return self._isFalloutPossibleOn(tile)

        return False

    def _isForestPossibleOn(self, tile):
        """Grassland, Grassland (Hills), Plains, Plains (Hills), Tundra and Tundra (Hills)."""
        if tile.terrain == TerrainType.tundra or tile.terrain == TerrainType.grass or tile.terrain == TerrainType.plains:
            return True

        return False

    def _isRainforestPossibleOn(self, tile):
        """Modifies Plains and Plains (Hills)."""
        if tile.terrain == TerrainType.plains:
            return True

        return False

    def _isFloodplainsPossibleOn(self, tile):
        """Floodplains modifies Deserts and also Plains and Grassland."""
        if tile.is_hills:
            return False

        if tile.terrain in [TerrainType.desert, TerrainType.grass, TerrainType.plains]:
            return True

        return False

    def _isMarshPossibleOn(self, tile):
        """Marsh modifies Grassland"""
        if tile.is_hills:
            return False

        if tile.terrain == TerrainType.grass:
            return True

        return False

    def _isOasisPossibleOn(self, tile):
        """Oasis modifies Desert"""
        if tile.is_hills:
            return False

        if tile.terrain == TerrainType.desert:
            return True

        return False

    def _isReefPossibleOn(self, tile):
        """
            checks if feature reef is possible on tile
            https://civilization.fandom.com/wiki/Reef_(Civ6)

            @param tile: tile to check
            @return: True, if feature reef is possible on tile
        """
        if not tile.isWater():
            return False

        if tile.terrain != TerrainType.shore:
            return False

        return True

    def _isIcePossibleOn(self, tile):
        """Ice modifies Ocean and Shore"""
        if tile.isWater():
            return True

        return False

    def _isAtollPossibleOn(self, tile):
        """Atoll modifies Ocean and Shore"""
        if tile.isWater():
            return True

        return False

    def _isVolcanoPossibleOn(self, tile):
        """Volcano modifies Mountains"""
        if tile.feature == FeatureType.mountains:
            return True

        return False

    def _isMountainPossibleOn(self, tile):
        """Mountain modifies hilly Desert, Grassland, Plains, Tundra and Snow"""
        if tile.is_hills:
            return False

        if tile.terrain in [TerrainType.desert, TerrainType.grass, TerrainType.plains, TerrainType.tundra, TerrainType.snow]:
            return True

        return False

    def _isLakePossibleOn(self, tile):
        """Lake modifies all non-hilly terrain"""
        if tile.is_hills:
            return False

        if tile.isWater():
            return False

        return True

    def _isFalloutPossibleOn(self, tile):
        """Fallout modifies all land tiles"""
        if tile.isWater():
            return False

        return True

    def isNaturalWonder(self):
        return self.data().is_wonder

    def textures(self):
        if self == FeatureType.none:
            return ['feature_none@3x.png']

        if self == FeatureType.atoll:
            return ['feature_atoll@3x.png']

        if self == FeatureType.fallout:
            return ['feature_fallout@3x.png']

        if self == FeatureType.floodplains:
            return ['feature_floodplains@3x.png']

        if self == FeatureType.forest:
            return ['feature_forest1@3x.png', 'feature_forest2@3x.png']

        if self == FeatureType.ice:
            return ['feature_ice1@3x.png', 'feature_ice2@3x.png', 'feature_ice3@3x.png', 'feature_ice4@3x.png', 'feature_ice5@3x.png', 'feature_ice6@3x.png']

        if self == FeatureType.marsh:
            return ['feature_marsh1@3x.png', 'feature_marsh2@3x.png']

        if self == FeatureType.mountains:
            return ['feature_mountains1@3x.png', 'feature_mountains2@3x.png', 'feature_mountains3@3x.png']

        if self == FeatureType.oasis:
            return ['feature_oasis@3x.png']

        if self == FeatureType.pine:
            return ['feature_pine1@3x.png', 'feature_pine2@3x.png']

        if self == FeatureType.rainforest:
            return ['feature_rainforest1@3x.png', 'feature_rainforest2@3x.png', 'feature_rainforest3@3x.png', 'feature_rainforest4@3x.png', 'feature_rainforest5@3x.png', 'feature_rainforest6@3x.png', 'feature_rainforest7@3x.png', 'feature_rainforest8@3x.png', 'feature_rainforest9@3x.png']

        if self == FeatureType.reef:
            return ['feature_reef1@3x.png', 'feature_reef2@3x.png', 'feature_reef3@3x.png']

        if self == FeatureType.lake:
            return []

        if self == FeatureType.volcano:
            return []

        # natural wonders

        if self == FeatureType.mountEverest:
            return []

        if self == FeatureType.mountKilimanjaro:
            return []

        return []


class ResourceUsage(ExtendedEnum):
    bonus = 'bonus'
    strategic = 'strategic'
    luxury = 'luxury'
    artifacts = 'artifacts'

    def amenities(self) -> int:

        if self == ResourceUsage.luxury:
            return 4

        return 0


class ResourceTypeData:
    def __init__(self, name: str, usage: ResourceUsage, reveal_tech, reveal_civic, placement_order: int, base_amount: int, place_on_hills: bool, place_on_river_side: bool, place_on_flatlands: bool, place_on_features, place_on_feature_terrains, place_on_terrains):
        self.name = name
        self.usage = usage
        self.reveal_tech = reveal_tech
        self.reveal_civic = reveal_civic
        self.placement_order = placement_order
        self.base_amount = base_amount

        self.place_on_hills = place_on_hills
        self.place_on_river_side = place_on_river_side
        self.place_on_flatlands = place_on_flatlands
        self.place_on_features = place_on_features
        self.place_on_feature_terrains = place_on_feature_terrains
        self.place_on_terrains = place_on_terrains


class ResourceType(ExtendedEnum):
    # default
    none = 'none'

    # bonus
    wheat = 'wheat'
    rice = 'rice'
    deer = 'deer'
    sheep = 'sheep'
    copper = 'copper'
    stone = 'stone'  # https://civilization.fandom.com/wiki/Stone_(Civ6)
    banana = 'banana'
    cattle = 'cattle'
    fish = 'fish'

    # luxury
    citrus = 'citrus'
    whales = 'whales'

    # strategic
    horses = 'horses'
    iron = 'iron'  # https://civilization.fandom.com/wiki/Iron_(Civ6)
    coal = 'coal'  # https://civilization.fandom.com/wiki/Coal_(Civ6)
    oil = 'oil'  # https://civilization.fandom.com/wiki/Oil_(Civ6)
    aluminum = 'aluminium'  # https://civilization.fandom.com/wiki/Aluminum_(Civ6)
    uranium = 'uranium'  # https://civilization.fandom.com/wiki/Uranium_(Civ6)
    niter = 'niter'  # https://civilization.fandom.com/wiki/Niter_(Civ6)

    # artifacts
    antiquitySite = 'antiquitySite'  # https://civilization.fandom.com/wiki/Antiquity_Site_(Civ6)
    shipwreck = 'shipwreck'  # https://civilization.fandom.com/wiki/Shipwreck_(Civ6)

    def name(self) -> str:
        return self._data().name

    def usage(self) -> ResourceUsage:
        return self._data().usage

    def placementOrder(self) -> int:
        return self._data().placement_order

    def _data(self) -> ResourceTypeData:
        # default
        if self == ResourceType.none:
            return ResourceTypeData(
                'none',
                ResourceUsage.bonus,
                None,
                None,
                -1,
                0,
                False,
                False,
                False,
                [],
                [],
                []
            )

        # bonus
        if self == ResourceType.wheat:
            return ResourceTypeData(
                name='Wheat',
                usage=ResourceUsage.bonus,
                reveal_tech=TechType.pottery,
                reveal_civic=None,
                placement_order=4,
                base_amount=18,
                place_on_hills=False,
                place_on_river_side=False,
                place_on_flatlands=True,
                place_on_features=[FeatureType.floodplains],
                place_on_feature_terrains=[TerrainType.desert],
                place_on_terrains=[TerrainType.plains]
            )
        elif self == ResourceType.rice:
            return ResourceTypeData(
                name='Rice',
                usage=ResourceUsage.bonus,
                reveal_tech=TechType.pottery,
                reveal_civic=None,
                placement_order=4,
                base_amount=14,
                place_on_hills=False,
                place_on_river_side=False,
                place_on_flatlands=True,
                place_on_features=[FeatureType.marsh],
                place_on_feature_terrains=[TerrainType.grass],
                place_on_terrains=[TerrainType.grass]
            )
        elif self == ResourceType.deer:
            return ResourceTypeData(
                name='Deer',
                usage=ResourceUsage.bonus,
                reveal_tech=TechType.animalHusbandry,
                reveal_civic=None,
                placement_order=4,
                base_amount=16,
                place_on_hills=False,
                place_on_river_side=False,
                place_on_flatlands=True,
                place_on_features=[FeatureType.forest],
                place_on_feature_terrains=[TerrainType.grass, TerrainType.plains, TerrainType.tundra, TerrainType.snow],
                place_on_terrains=[TerrainType.tundra]
            )
        elif self == ResourceType.sheep:
            return ResourceTypeData(
                name='Sheep',
                usage=ResourceUsage.bonus,
                reveal_tech=None,
                reveal_civic=None,
                placement_order=4,
                base_amount=20,
                place_on_hills=True,
                place_on_river_side=True,
                place_on_flatlands=False,
                place_on_features=[FeatureType.forest],
                place_on_feature_terrains=[TerrainType.grass, TerrainType.plains, TerrainType.tundra, TerrainType.snow],
                place_on_terrains=[TerrainType.tundra]
            )
        elif self == ResourceType.copper:
            return ResourceTypeData(
                name='Copper',
                usage=ResourceUsage.bonus,
                reveal_tech=None,
                reveal_civic=None,
                placement_order=4,
                base_amount=6,
                place_on_hills=True,
                place_on_river_side=False,
                place_on_flatlands=False,
                place_on_features=[],
                place_on_feature_terrains=[],
                place_on_terrains=[TerrainType.grass, TerrainType.plains, TerrainType.desert, TerrainType.tundra]
            )
        elif self == ResourceType.stone:
            return ResourceTypeData(
                name='Stone',
                usage=ResourceUsage.bonus,
                reveal_tech=None,
                reveal_civic=None,
                placement_order=4,
                base_amount=12,
                place_on_hills=True,
                place_on_river_side=False,
                place_on_flatlands=True,
                place_on_features=[],
                place_on_feature_terrains=[],
                place_on_terrains=[TerrainType.grass]
            )
        elif self == ResourceType.banana:
            return ResourceTypeData(
                name='Banana',
                usage=ResourceUsage.bonus,
                reveal_tech=None,
                reveal_civic=None,
                placement_order=4,
                base_amount=2,
                place_on_hills=False,
                place_on_river_side=False,
                place_on_flatlands=True,
                place_on_features=[FeatureType.rainforest],
                place_on_feature_terrains=[TerrainType.grass, TerrainType.plains],
                place_on_terrains=[]
            )
        elif self == ResourceType.cattle:
            return ResourceTypeData(
                name='Cattle',
                usage=ResourceUsage.bonus,
                reveal_tech=None,
                reveal_civic=None,
                placement_order=4,
                base_amount=22,
                place_on_hills=False,
                place_on_river_side=True,
                place_on_flatlands=True,
                place_on_features=[],
                place_on_feature_terrains=[],
                place_on_terrains=[TerrainType.grass]
            )
        elif self == ResourceType.fish:
            return ResourceTypeData(
                name='Fish',
                usage=ResourceUsage.bonus,
                reveal_tech=None,
                reveal_civic=None,
                placement_order=4,
                base_amount=36,
                place_on_hills=False,
                place_on_river_side=False,
                place_on_flatlands=False,
                place_on_features=[FeatureType.lake],
                place_on_feature_terrains=[],
                place_on_terrains=[TerrainType.shore]
            )

        # luxury
        elif self == ResourceType.citrus:
            return ResourceTypeData(
                name='Citrus',
                usage=ResourceUsage.luxury,
                reveal_tech=None,
                reveal_civic=None,
                placement_order=3,
                base_amount=2,
                place_on_hills=False,
                place_on_river_side=False,
                place_on_flatlands=True,
                place_on_features=[],
                place_on_feature_terrains=[],
                place_on_terrains=[TerrainType.grass, TerrainType.plains]
            )
        elif self == ResourceType.whales:
            return ResourceTypeData(
                name='Whales',
                usage=ResourceUsage.luxury,
                reveal_tech=None,
                reveal_civic=None,
                placement_order=3,
                base_amount=6,
                place_on_hills=False,
                place_on_river_side=False,
                place_on_flatlands=True,
                place_on_features=[],
                place_on_feature_terrains=[],
                place_on_terrains=[TerrainType.shore]
            )

        # strategic
        elif self == ResourceType.horses:
            return ResourceTypeData(
                name='Horses',
                usage=ResourceUsage.strategic,
                reveal_tech=None,
                reveal_civic=None,
                placement_order=1,
                base_amount=14,
                place_on_hills=False,
                place_on_river_side=True,
                place_on_flatlands=True,
                place_on_features=[],
                place_on_feature_terrains=[],
                place_on_terrains=[TerrainType.grass, TerrainType.plains, TerrainType.tundra]
            )
        elif self == ResourceType.iron:
            return ResourceTypeData(
                name='Iron',
                usage=ResourceUsage.strategic,
                reveal_tech=TechType.bronzeWorking,
                reveal_civic=None,
                placement_order=0,
                base_amount=12,
                place_on_hills=False,
                place_on_river_side=True,
                place_on_flatlands=True,
                place_on_features=[],
                place_on_feature_terrains=[],
                place_on_terrains=[TerrainType.grass, TerrainType.plains, TerrainType.tundra, TerrainType.desert, TerrainType.snow]
            )
        elif self == ResourceType.coal:
            return ResourceTypeData(
                name='Coal',
                usage=ResourceUsage.strategic,
                reveal_tech=TechType.industrialization,
                reveal_civic=None,
                placement_order=2,
                base_amount=10,
                place_on_hills=True,
                place_on_river_side=False,
                place_on_flatlands=False,
                place_on_features=[],
                place_on_feature_terrains=[],
                place_on_terrains=[TerrainType.plains, TerrainType.grass]
            )
        elif self == ResourceType.oil:
            return ResourceTypeData(
                name='Oil',
                usage=ResourceUsage.strategic,
                reveal_tech=TechType.refining,
                reveal_civic=None,
                placement_order=2,
                base_amount=8,
                place_on_hills=False,
                place_on_river_side=True,
                place_on_flatlands=True,
                place_on_features=[FeatureType.rainforest, FeatureType.marsh],
                place_on_feature_terrains=[TerrainType.grass, TerrainType.plains],
                place_on_terrains=[TerrainType.desert, TerrainType.tundra, TerrainType.snow, TerrainType.shore]
            )
        elif self == ResourceType.aluminum:
            return ResourceTypeData(
                name='Aluminum',
                usage=ResourceUsage.strategic,
                reveal_tech=None,
                reveal_civic=None,
                placement_order=2,
                base_amount=8,
                place_on_hills=True,
                place_on_river_side=False,
                place_on_flatlands=False,
                place_on_features=[],
                place_on_feature_terrains=[TerrainType.plains],
                place_on_terrains=[TerrainType.grass, TerrainType.plains]
            )
        elif self == ResourceType.uranium:
            return ResourceTypeData(
                name='Uranium',
                usage=ResourceUsage.strategic,
                reveal_tech=None,
                reveal_civic=None,
                placement_order=2,
                base_amount=4,
                place_on_hills=False,
                place_on_river_side=True,
                place_on_flatlands=True,
                place_on_features=[FeatureType.rainforest, FeatureType.marsh, FeatureType.forest],
                place_on_feature_terrains=[TerrainType.grass, TerrainType.plains, TerrainType.desert, TerrainType.tundra, TerrainType.snow],
                place_on_terrains=[TerrainType.grass, TerrainType.plains, TerrainType.desert, TerrainType.tundra, TerrainType.snow]
            )
        elif self == ResourceType.niter:
            return ResourceTypeData(
                name='Niter',
                usage=ResourceUsage.strategic,
                reveal_tech=None,
                reveal_civic=None,
                placement_order=2,
                base_amount=8,
                place_on_hills=False,
                place_on_river_side=False,
                place_on_flatlands=True,
                place_on_features=[],
                place_on_feature_terrains=[],
                place_on_terrains=[TerrainType.grass, TerrainType.plains, TerrainType.desert, TerrainType.tundra]
            )

        # artifacts
        elif self == ResourceType.antiquitySite:
            return ResourceTypeData(
                name='Antiquity Site',
                usage=ResourceUsage.artifacts,
                reveal_tech=None,
                reveal_civic=None,
                placement_order=-1,
                base_amount=0,
                place_on_hills=True,
                place_on_river_side=True,
                place_on_flatlands=True,
                place_on_features=[],
                place_on_feature_terrains=[],
                place_on_terrains=[TerrainType.grass, TerrainType.plains, TerrainType.desert, TerrainType.tundra, TerrainType.snow]
            )
        elif self == ResourceType.shipwreck:
            return ResourceTypeData(
                name='Shipwreck',
                usage=ResourceUsage.artifacts,
                reveal_tech=None,
                reveal_civic=None,
                placement_order=-1,
                base_amount=0,
                place_on_hills=False,
                place_on_river_side=False,
                place_on_flatlands=False,
                place_on_features=[],
                place_on_feature_terrains=[],
                place_on_terrains=[TerrainType.shore, TerrainType.ocean]
            )

        raise AttributeError(f'cant determine data of {self}')

    def canBePlacedOnFeature(self, feature: FeatureType) -> bool:
        return feature in self._data().place_on_features

    def canBePlacedOnFeatureTerrain(self, terrain: TerrainType) -> bool:
        return terrain in self._data().place_on_feature_terrains

    def canBePlacedOnTerrain(self, terrain: TerrainType) -> bool:
        return terrain in self._data().place_on_terrains

    def canBePlacedOnHills(self) -> bool:
        return self._data().place_on_hills

    def canBePlacedOnFlatlands(self):
        return self._data().place_on_flatlands

    def baseAmount(self):
        return self._data().base_amount

    def absoluteVarPercent(self):
        if self == ResourceType.fish:
            return 10

        return 25

    def revealTech(self):
        """
            returns the tech that reveals the resource
            :return: tech that is needed to reveal the resource
        """
        return self._data().reveal_tech

    def revealCivic(self):
        """
            returns the civic that reveals the resource
            :return: civic that is needed to reveal the resource
        """
        return self._data().reveal_civic

    def __str__(self):
        return self.value


class ClimateZone(ExtendedEnum):
    polar = 'polar'
    sub_polar = 'sub_polar'
    temperate = 'temperate'
    sub_tropic = 'sub_tropic'
    tropic = 'tropic'

    def moderate(self):
        if self == ClimateZone.polar:
            return ClimateZone.sub_polar
        elif self == ClimateZone.sub_polar:
            return ClimateZone.temperate
        elif self == ClimateZone.temperate:
            return ClimateZone.sub_tropic
        elif self == ClimateZone.sub_tropic:
            return ClimateZone.tropic
        else:
            return ClimateZone.tropic


class MovementType(ExtendedEnum):
    immobile = 'immobile'
    walk = 'walk'
    swim = 'swim'
    swimShallow = 'swimShallow'

    max = 1000


class RouteType(ExtendedEnum):
    none = 'none'
    ancientRoad = 'ancientRoad'
    classicalRoad = 'classicalRoad'
    industrialRoad = 'industrialRoad'
    modernRoad = 'modernRoad'

    def movementCost(self):
        if self == RouteType.none:
            return 200
        elif self == RouteType.ancientRoad:
            # Starting road, well-packed dirt. Most terrain costs 1 MP; crossing rivers still costs 3 MP.
            return 1
        elif self == RouteType.classicalRoad:
            # Adds bridges over rivers; crossing costs reduced to only 1 MP.
            return 1
        elif self == RouteType.industrialRoad:
            # Paved roads are developed; 0.75 MP per tile.
            return 0.75
        elif self == RouteType.modernRoad:
            # Asphalted roads are developed; 0.50 MP per tile.
            return 0.5
