# accounts/models.py
from datetime import date

from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# parent profile photo save path
def parent_profile_photo_path(instance, filename):
    return f"parents/{instance.parent.username}/profile_photo/{filename[:6]}"


# child profile photo save  path
def child_profile_photo_path(instance, filename):
    return f"children/{instance.child.username}/avatar/{filename[-9:]}"


class ParentManager(UserManager):
    """Custom Parent Manager"""

    def get_queryset(self):
        return super().get_queryset().filter(user_type=User.UserType.PARENT)


class ChildManager(UserManager):
    """Custom Parent Manager"""

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

    @property
    def is_parent(self):
        if self.user_type == User.UserType.PARENT:
            return True
        else:
            return False

    @property
    def is_child(self):
        if self.user_type == User.UserType.CHILD:
            return True
        else:
            return False

    def __str__(self):
        return self.username


class ParentProfile(models.Model):
    """Parent Profile Model"""

    # choices for parent gender
    class ParentGender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    parent = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(
        max_length=1, choices=ParentGender.choices, default=ParentGender.MALE
    )
    photo = models.ImageField(
        upload_to=parent_profile_photo_path,
        blank=True,
        null=True,
    )

    @property
    def completion_percentage(self):
        # Define the fields to be checked for completion
        profile_fields = [
            self.phone_number,
            self.address,
            self.parent.first_name,
            self.parent.last_name,
            self.photo,
        ]

        # Calculate the number of completed fields
        completed_fields = sum(1 for field in profile_fields if field)

        # Calculate the percentage of completion
        if len(profile_fields) > 0:
            completion_percentage = (completed_fields / len(profile_fields)) * 100
        else:
            completion_percentage = (
                100  # Profile is considered complete if there are no fields to complete
            )

        return int(completion_percentage)

    @property
    def unreviewed_alerts(self):
        unreviewed = self.searchalert_set.filter(been_reviewed=False)
        return unreviewed.count()

    @property
    def unreviewed_unban_requests(self):
        unreviewed = list()
        for childprofile in self.childprofile_set.all():
            unbanrequests = childprofile.unbanrequest_set.filter(been_reviewed=False)
            if unbanrequests:
                for unbanrequest in unbanrequests:
                    unreviewed.append(unbanrequest)

        return len(unreviewed)

    def __str__(self):
        return f"{self.parent.username}'s profile"

    class Meta:
        ordering = ["parent"]


# choices for account status
class AccountStatus(models.TextChoices):
    ACTIVE = "AC", "Active"
    BANNED = "BN", "Banned"


class ChildProfile(models.Model):
    """Child Profile Model"""

    # choices for child gender
    class ChildGender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    child = models.OneToOneField(User, on_delete=models.CASCADE)
    parent_profile = models.ForeignKey(
        ParentProfile, on_delete=models.CASCADE, null=True
    )
    date_of_birth = models.DateField(
        blank=False,
        null=False,
        help_text="Only children beween the ages of 9 and 15 are allowed to register.",
    )
    account_status = models.CharField(
        max_length=2, choices=AccountStatus.choices, default=AccountStatus.ACTIVE
    )
    gender = models.CharField(
        max_length=1, choices=ChildGender.choices, default=ChildGender.MALE
    )

    avatar = models.ImageField(
        upload_to=child_profile_photo_path,
        blank=True,
        null=True,
    )
    last_seen = models.DateTimeField(default=timezone.now, editable=False)

    @property
    def banned(self):
        if self.account_status == AccountStatus.BANNED:
            return True
        else:
            return False

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

    def save(self, *args, **kwargs):
        min_age = 6
        max_age = 17

        if not min_age <= self.age <= max_age:
            raise ValidationError(
                _(f"Children must be between {min_age} and {max_age} years old.")
            )

        super(ChildProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.child.username}'s profile"

    class Meta:
        ordering = ["child"]


class Confirmation(models.Model):
    """Parent Email Verification Model"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": User.UserType.PARENT},
    )
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField(null=True)

    @property
    def expired(self):
        # Compare the current time with 'expires_on'
        if self.expires_on <= timezone.now():
            return True
        else:
            return False

    def __str__(self):
        return f"{self.user.username}'s profile"

    def regenerate_token(self):
        # Generate a new token
        new_token = token_generator.make_token(self.user)

        # Update the token and expiration time
        self.token = new_token
        self.expires_on = timezone.now() + timezone.timedelta(minutes=30)
        self.save()

        return self.token

    class Meta:
        ordering = ["user"]


class AlertLevel(models.TextChoices):
    STRICT = "S", "Strict"
    MODERATE = "M", "Moderate"
    LOW = "L", "Low"


class ChildSettings(models.Model):
    child = models.OneToOneField(ChildProfile, on_delete=models.CASCADE, null=True)
    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE, null=True)

    # Alert and Filter Levels
    alert_level = models.CharField(
        max_length=10,
        choices=AlertLevel.choices,
        default=AlertLevel.MODERATE,
    )

    # Limit Activity Based on Time and Frequency of Search
    search_time_start = models.TimeField(
        null=True,
        blank=True,
        default=timezone.make_aware(
            timezone.datetime(1, 1, 1, 8, 0), timezone.get_current_timezone()
        ),
    )
    search_time_end = models.TimeField(
        null=True,
        blank=True,
        default=timezone.make_aware(
            timezone.datetime(1, 1, 1, 18, 0), timezone.get_current_timezone()
        ),
    )
    search_frequency_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of searches allowed within the time period",
    )

    def __str__(self):
        return f"Search Settings for {self.child.username}"
