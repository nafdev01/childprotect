from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import child_required, parent_required
from accounts.notifications import (
    send_email_newsletter_subscription,
    send_email_succesful_contact,
)

from .models import Comment, Contact, Post, Subscriber, TypeOfComment


@parent_required
def post_list(request):
    posts = Post.objects.all()
    parent = request.user
    parent_profile = parent.parentprofile

    template_name = "forum/forum.html"
    context = {"posts": posts, "parent": parent, "parent_profile": parent_profile}

    return render(request, template_name=template_name, context=context)


@parent_required
def create_post(request):
    parent = request.user
    parent_profile = parent.parentprofile

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        new_post = Post.objects.create(title=title, content=content, created_by=parent)
        new_post.save()
        messages.success(request, f"You have created a new post {title}")

    return redirect("forum:post_list")


@parent_required
def post_detail(request, post_id):
    parent = request.user
    parent_profile = parent.parentprofile

    post = get_object_or_404(Post, id=post_id)
    og_comments = Comment.original.filter(post=post)

    template_name = "forum/post_detail.html"
    context = {
        "post": post,
        "parent": parent,
        "parent_profile": parent_profile,
        "og_comments": og_comments,
    }
    return render(request, template_name=template_name, context=context)


@parent_required
def create_og_comment(request, post_id):
    parent = request.user
    parent_profile = parent.parentprofile

    if request.method == "POST":
        content = request.POST.get("content")
        if post_id:
            post = Post.objects.get(id=post_id)
            new_comment = Comment.objects.create(
                content=content,
                post=post,
                type_of_comment=TypeOfComment.ORIGINAL,
            )
            new_comment.save()
            messages.success(request, f"You have replied to a post")

    return redirect("forum:post_detail", post_id=post.id)


@parent_required
def reply_to_comment(request, comment_id):
    parent = request.user
    parent_profile = parent.parentprofile

    if request.method == "POST":
        content = request.POST.get("content")
        if comment_id:
            comment = Comment.original.get(id=comment_id)
            post = comment.post
            new_reply = Comment.objects.create(
                content=content,
                reply_to=comment,
                type_of_comment=TypeOfComment.REPLY,
            )
            new_reply.save()
            messages.success(request, f"You have replied to a post")

    return redirect("forum:post_detail", post_id=post.id)


def add_subscriber(request):
    if request.method == "POST":
        email = request.POST.get("email")
        # Check if a subscriber with the provided email already exists
        existing_subscriber = Subscriber.objects.filter(email=email).first()
        if existing_subscriber:
            messages.success(
                request, f"You are already subscribed to our newsletter."
            )

        else:
            subscriber = Subscriber.objects.create(email=email)
            subscriber.save()
            send_email_newsletter_subscription(request, subscriber.email)
    else:
        messages.error(request, f"You cannot access this page")

    return redirect("home")


def contact_message(request):
    if request.method == "POST":
        name = request.POST["name"]
        subject = request.POST["subject"]
        email = request.POST["email"]
        message = request.POST["message"]

        # Save the data to the database using your Contact model
        contact = Contact.objects.create(
            name=name, subject=subject, email=email, message=message
        )
        contact.save()
        send_email_succesful_contact(request, name, email, message, subject)
    else:
        messages.error(request, f"You cannot access this page")

    return redirect("contact")
