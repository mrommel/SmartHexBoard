from abc import ABC

from rest_framework import serializers


class TechInfoSerializer(serializers.Serializer, ABC):
    name = serializers.CharField()
    turns = serializers.IntField()
    eureka = serializers.CharField()
    col = serializers.IntField()
    row = serializers.IntField()
