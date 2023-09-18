# accounts/models.py
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.conf import settings
from datetime import date
from django.utils import timezone
from django.db import models


class ParentManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(user_type=User.UserType.PARENT)


class ChildManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(user_type=User.UserType.CHILD)


class User(AbstractUser):

    """Model definition for Users."""

    # choices for user type
    class UserType(models.TextChoices):
        PARENT = "PR", "Parent"
        CHILD = "CH", "Child"

    # Add other fields common to both parent and child users
    user_type = models.CharField(max_length=2, choices=UserType.choices, editable=False)

    # The default manager.
    objects = UserManager()
    # The parent users manager.
    parents = ParentManager()  # Our custom manager.
    # The child users manager.
    children = ChildManager()  # Our custom manager.

    def is_parent(self):
        if self.user_type == User.UserType.PARENT:
            return True
        else:
            return False

    def is_child(self):
        if self.user_type == User.UserType.CHILD:
            return True
        else:
            return False

    def __str__(self):
        return self.username


class ParentProfile(models.Model):
    # choices for parent gender
    class ParentGender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    parent = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(
        max_length=1, choices=ParentGender.choices, default=ParentGender.MALE
    )

    def __str__(self):
        return f"{self.parent.username}'s profile"

    class Meta:
        ordering = ["parent"]


class ChildProfile(models.Model):
    # choices for account status
    class AccountStatus(models.TextChoices):
        ACTIVE = "AC", "Active"
        BANNED = "BN", "Banned"

    # choices for child gender
    class ChildGender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    child = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent_profile = models.ForeignKey(
        ParentProfile, on_delete=models.CASCADE, null=True
    )
    date_of_birth = models.DateField(blank=False, null=False)
    account_status = models.CharField(max_length=2, choices=AccountStatus.choices)
    gender = models.CharField(
        max_length=1, choices=ChildGender.choices, default=ChildGender.MALE
    )

    @property
    def age(self):
        today = date.today()
        age = (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )
        return age

    def __str__(self):
        return f"{self.child.username}'s profile"

    class Meta:
        ordering = ["child"]
