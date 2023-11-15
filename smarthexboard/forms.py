from django import forms


class CreateGameForm(forms.Form):
    leader = forms.CharField(label="leader", max_length=32)
    handicap = forms.CharField(label="handicap", max_length=32)
    mapSize = forms.CharField(label="mapSize", max_length=32)
    mapType = forms.CharField(label="mapType", max_length=32)
