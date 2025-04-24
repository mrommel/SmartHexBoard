import cv2
import numpy as np
from django.db import models
from django.utils.translation import gettext_lazy as _


class ObjectType(models.TextChoices):
	UNKNOWN = 'UNK', _('Unknown')

	LAYER = 'LAY', _('Layer')
	OBJECT = 'OBJ', _('Object')


class Object(models.Model):
	name = models.CharField(max_length=64)
	file = models.FileField(upload_to='objects')
	type = models.CharField(
		max_length=3,
		choices=ObjectType.choices,
		default=ObjectType.UNKNOWN,
	)
	# meta data
	width = models.PositiveIntegerField()
	height = models.PositiveIntegerField()

	objects = models.Manager()

	def clean(self):
		im = cv2.imdecode(np.asarray(bytearray(self.file.file.read()), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
		h, w, c = im.shape
		self.width = w
		self.height = h

	def __str__(self):
		return f'{self.name}'


class Asset(models.Model):
	"""to be exported"""
	name = models.CharField(max_length=64)
	hint = models.CharField(max_length=256, blank=True)
	asset_objects = models.ManyToManyField(Object, through="AssetMembership")

	width = models.PositiveIntegerField()
	height = models.PositiveIntegerField()

	objects = models.Manager()

	def render(self):
		canvas_image = np.zeros((self.height, self.width, 4), dtype='uint8')

		assets = AssetMembership.objects.filter(asset=self).order_by('z_index')

		# Render all objects
		for asset in assets:
			asset_object = asset.object
			asset_object_x = asset.x
			asset_object_y = asset.y

			# object_image = cv2.imread(asset_object.file, cv2.IMREAD_UNCHANGED)
			object_image = cv2.imdecode(np.asarray(bytearray(asset_object.file.file.read()), dtype=np.uint8), cv2.IMREAD_UNCHANGED)

			object_height, object_width, object_channels = object_image.shape

			print(f'Render {asset_object} => {object_width}x{object_height} with {object_channels} channels')

			for y in range(object_height):
				for x in range(object_width):
					# (if you don't do this, the black background will also be copied)
					if object_image[y, x, 3] > 0:
						canvas_image[y + asset_object_y, x + asset_object_x, :] = object_image[y, x, :]

		# Encode the image in PNG format
		_, image_encoded = cv2.imencode('.png', canvas_image)

		# Return the image as cv2 image
		return image_encoded

	def __str__(self):
		return f'{self.name}'


class AssetMembership(models.Model):
	asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
	object = models.ForeignKey(Object, on_delete=models.CASCADE)

	x = models.IntegerField()
	y = models.IntegerField()
	z_index = models.IntegerField()  # z-index
	scale = models.FloatField()

	objects = models.Manager()

	def __str__(self):
		return f'{self.asset.name} - {self.object.name}'
