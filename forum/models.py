# forum/models.py
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from accounts.models import User


class Post(models.Model):
    created_by = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": User.UserType.PARENT},
        to_field="username",
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)

    def og_comments(self):
        return Comment.original.filter(post=self)

    def __str__(self):
        return f"{self.title[:20]}"

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-posted_on"]


class TypeOfComment(models.TextChoices):
    REPLY = "R", "Reply"
    ORIGINAL = "O", "Original"


class Comment(models.Model):
    class OriginalManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(type_of_comment=TypeOfComment.ORIGINAL)

    class ReplyManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(type_of_comment=TypeOfComment.REPLY)

    content = models.TextField()
    post = models.ForeignKey("Post", null=True, on_delete=models.CASCADE)
    reply_to = models.ForeignKey("self", null=True, on_delete=models.CASCADE)
    type_of_comment = models.CharField(
        max_length=1,
        choices=TypeOfComment.choices,
        default=TypeOfComment.REPLY,
    )

    objects = models.Manager()
    original = OriginalManager()
    replies = ReplyManager()

    def reply_comments(self):
        return Comment.replies.filter(reply_to=self.id)

    def save(self, *args, **kwargs):
        if self.post and self.reply_to:
            raise ValidationError(
                "Both post and reply_to fields cannot be filled at the same time."
            )
        elif self.post and not self.reply_to:
            self.type_of_comment = TypeOfComment.ORIGINAL
        elif self.reply_to and not self.post:
            self.type_of_comment = TypeOfComment.REPLY
        super(Comment, self).save(*args, **kwargs)

    def __str__(self):
        return f"comment {self.content[:20]}"

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"


class Subscriber(models.Model):
    email = models.EmailField(max_length=254, unique=True)
    subscribed_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.email}"

    class Meta:
        verbose_name = "Subscriber"
        verbose_name_plural = "Subscribers"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    responded = models.BooleanField(default=False)
    contact_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"


class ContactResponse(models.Model):
    contact = models.OneToOneField(Contact, null=True, on_delete=models.CASCADE)
    responded = models.BooleanField(default=False)
    responded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.contact}"

    class Meta:
        verbose_name = "Contact Response"
        verbose_name_plural = "Contact Responses"


class Message(models.Model):
    username = models.CharField(max_length=100)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} sent {self.message}"
