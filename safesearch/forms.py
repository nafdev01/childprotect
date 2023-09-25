# safesearch/forms.py
from django import forms
from .models import BannedWord


class BannedCSVForm(forms.Form):
    csv_file = forms.FileField()


class BannedWordForm(forms.ModelForm):
    class Meta:
        model = BannedWord
        fields = ["word", "reason"]
