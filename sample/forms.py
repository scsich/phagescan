
import django.forms as forms
from django.forms.fields import CharField


class SimpleSampleSearchForm(forms.Form):
	search_string = CharField(min_length=3, max_length=254,
	                          widget=forms.TextInput(attrs={'placeholder': "MD5/SHA256/Filename/Infection Name",
                                                            "class": "input-xxlarge"}))
