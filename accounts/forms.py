from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.conf import settings
from .models import ChildProfile, User, ParentProfile
from .widgets import DatePickerInput, TimePickerInput, DateTimePickerInput


class ParentRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
        field_classes = {"username": UsernameField}


# form for editing a user object
class ParentProfileForm(forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = ["phone_number", "address", "gender"]


class ChildRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name")
        field_classes = {"username": UsernameField}


# form for editing a user object
class ChildProfileForm(forms.ModelForm):
    class Meta:
        model = ChildProfile
        fields = ["date_of_birth", "gender"]
        widgets = {
            "date_of_birth": DatePickerInput(),
        }
