# safesearch/forms.py
from django import forms
from .models import BannedWord


class BannedWordForm(forms.ModelForm):
    class Meta:
        model = BannedWord
        fields = ["word", "reason"]
