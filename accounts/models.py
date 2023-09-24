# accounts/models.py
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from datetime import date
from django.utils import timezone
from django.db import models


class ParentManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(user_type=UserType.PARENT)


class ChildManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(user_type=UserType.CHILD)


# choices for user type
class UserType(models.TextChoices):
    PARENT = "PR", "Parent"
    CHILD = "CH", "Child"


# choices for account status
class AccountStatus(models.TextChoices):
    ACTIVATED = "AC", "Actived"
    NOTACTIVATED = "NA", "Not Activated"


# choices for account status
class ChildGender(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"


class User(AbstractUser):
    user_type = models.CharField(max_length=2, choices=UserType.choices, editable=False)
    account_status = models.CharField(
        max_length=2,
        choices=AccountStatus.choices,
        default=AccountStatus.NOTACTIVATED,
    )

    objects = UserManager()
    parents = ParentManager()
    children = ChildManager()

    @property
    def is_parent(self):
        if self.user_type == UserType.PARENT:
            return True
        else:
            return False

    @property
    def is_child(self):
        if self.user_type == UserType.CHILD:
            return True
        else:
            return False

    def __str__(self):
        return self.get_username()


class ParentProfile(models.Model):
    # choices for parent gender
    class ParentGender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    parent = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": UserType.PARENT},
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(
        max_length=1, choices=ParentGender.choices, default=ParentGender.MALE
    )

    @property
    def unreviewed_alerts(self):
        unreviewed = self.flaggedalert_set.filter(been_reviewed=False)
        return unreviewed.count()

    def __str__(self):
        return f"{self.parent.get_username()}'s profile"

    class Meta:
        ordering = ["parent"]


class ChildProfile(models.Model):
    # choices for child gender
    child = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": UserType.CHILD},
    )
    parent_profile = models.ForeignKey(
        ParentProfile,
        on_delete=models.CASCADE,
        null=True,
    )
    date_of_birth = models.DateField(blank=False, null=False)
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
        return f"{self.child.get_username()}'s profile"

    class Meta:
        ordering = ["child"]


class Confirmation(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": UserType.PARENT},
    )
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, null=True)
    expires_on = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.user.get_username()}'s confirmation token"

    def save(self, *args, **kwargs):
        if self.last_updated:
            self.expires_on = self.last_updated + timezone.timedelta(minutes=30)
        super(Confirmation, self).save(*args, **kwargs)

    class Meta:
        ordering = ["user"]
