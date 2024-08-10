from django import forms
from main.modules.functions import is_path_available
import json

class BoardForm(forms.Form):
    entrance = forms.JSONField()
    exit = forms.JSONField()
    walls = forms.JSONField()
    
    def clean(self):
        cleaned_data = super().clean()
        entrance = cleaned_data.get('entrance')
        exit = cleaned_data.get('exit')
        walls = cleaned_data.get('walls')
        
        if not entrance or not exit or not walls:
            raise forms.ValidationError("You didnt place exit and entrance")
        
        if len(walls) != 20:
            raise forms.ValidationError("You didnt place 20 walls")
        
        if not is_path_available(entrance, exit, walls):
            raise forms.ValidationError("There is no way from entrance to exit")
        
        return cleaned_data
