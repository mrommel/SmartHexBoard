""" django app configuration """
from django.apps import AppConfig


class SmarthexboardConfig(AppConfig):
	"""
		configuration class of the main django app
	"""
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'smarthexboard'
