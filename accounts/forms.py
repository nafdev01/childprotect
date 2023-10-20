from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from accounts.models import ChildProfile, User
from accounts.widgets import DatePickerInput
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate


class ParentRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")
        field_classes = {"username": UsernameField}


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
        help_texts = {
            "date_of_birth": "Only children beween the ages of 9 and 15 are allowed to register.",
        }


class LoginForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                try:
                    user_temp = User.objects.get(username=username)
                except:
                    user_temp = None

                if user_temp is not None:
                    self.confirm_login_allowed(user_temp)
                else:
                    raise forms.ValidationError(
                        self.error_messages["invalid_login"],
                        code="invalid_login",
                        params={"username": self.username_field.verbose_name},
                    )

        return self.cleaned_data
