from smarthexboard.map.base import ExtendedEnum


class FlavorType(ExtendedEnum):
	# default
	none = 'none'

	production = 'production'
	tileImprovement = 'tileImprovement'
	mobile = 'mobile'
	growth = 'growth'
	naval = 'naval'
	navalTileImprovement = 'navalTileImprovement'
	wonder = 'wonder'
	navalRecon = 'navalRecon'
	amenities = 'amenities'
	science = 'science'
	culture = 'culture'
	diplomacy = 'diplomacy'
	cityDefense = 'cityDefense'
	ranged = 'ranged'
	offense = 'offense'
	defense = 'defense'
	militaryTraining = 'militaryTraining'
	infrastructure = 'infrastructure'
	gold = 'gold'
	navalGrowth = 'navalGrowth'
	energy = 'energy'
	expansion = 'expansion'
	greatPeople = 'greatPeople'
	religion = 'religion'
	tourism = 'tourism'
	recon = 'recon'


class Flavor:
	def __init__(self, flavor: FlavorType, value: int):
		self.flavor = flavor
		self.value = value
