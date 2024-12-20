from django import forms
from django.core.exceptions import ValidationError
from .smarthexboardlib.game.baseTypes import HandicapType
from .smarthexboardlib.game.civilizations import LeaderType
from .smarthexboardlib.map.types import MapType, MapSize


class CreateGameForm(forms.Form):
    leader = forms.CharField(label="leader", max_length=32)
    handicap = forms.CharField(label="handicap", max_length=32)
    mapSize = forms.CharField(label="mapSize", max_length=32)
    mapType = forms.CharField(label="mapType", max_length=32)

    def clean(self):
        cleaned_data = super().clean()

        # check leader
        leader_cleaned = cleaned_data.get("leader")

        if leader_cleaned is not None:
            try:
                LeaderType.fromName(leader_cleaned)
            except:
                self.add_error("leader", f"Cannot map leader from '{leader_cleaned}' to LeaderType")

        # check handicap
        handicap_cleaned = cleaned_data.get("handicap")

        if handicap_cleaned is not None:
            try:
                HandicapType.fromName(handicap_cleaned)
            except:
                self.add_error("handicap", f"Cannot map handicap from '{handicap_cleaned}' to HandicapType")

        # check mapSize
        mapSize_cleaned = cleaned_data.get("mapSize")

        if mapSize_cleaned is not None:
            try:
                MapSize.fromName(mapSize_cleaned)
            except:
                self.add_error("mapSize", f"Cannot map mapSize from '{mapSize_cleaned}' to MapSize")

        # check mapType
        mapType_cleaned = cleaned_data.get("mapType")

        if mapType_cleaned is not None:
            try:
                MapType.fromName(mapType_cleaned)
            except:
                self.add_error("mapType", f"Cannot map mapType from '{mapType_cleaned}' to MapType")

        return

    def leaderValue(self) -> LeaderType:
        try:
            return LeaderType.fromName(self.data['leader'])
        except:
            raise Exception(f"Cannot map leader from '{self.data['leader']}' to LeaderType")

    def handicapValue(self):
        try:
            return HandicapType.fromName(self.data['handicap'])
        except:
            raise Exception(f"Cannot map handicap from '{self.data['handicap']}' to HandicapType")

    def mapSizeValue(self):
        try:
            return MapSize.fromName(self.data['mapSize'])
        except:
            raise Exception(f"Cannot map mapSize from '{self.data['mapSize']}' to MapSize")

    def mapTypeValue(self):
        try:
            return MapType.fromName(self.data['mapType'])
        except:
            raise Exception(f"Cannot map mapType from '{self.data['mapType']}' to MapType")
