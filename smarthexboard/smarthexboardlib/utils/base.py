def isinstance_string(variable, string):
	return variable.__class__.__name__ == string


def firstOrNone(array_or_list):
	return next(iter(array_or_list or []), None)


def secondOrNone(array_or_list):
	return array_or_list[1] if len(array_or_list) > 1 else None


def lastOrNone(array_or_list):
	return array_or_list[-1] if len(array_or_list) > 1 else None


def dictToArray(dictionary: dict):
	if isinstance(dictionary, dict):
		return [(k, dictionary[k]) for k in dictionary]

	raise Exception(f'can only convert dict to array but got {type(dictionary)}')


def clamp(value, lower, upper):
	return lower if value < lower else upper if value > upper else value
