from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.notifications import (
    send_email_newsletter_subscription,
    send_email_succesful_contact,
)
from .models import Post, Comment, TypeOfComment, Subscriber, Contact
from accounts.decorators import parent_required, child_required


@parent_required
def post_detail(request):
    posts = Post.objects.all()

    return render(
        request,
        "forum/forum.html",
        {"posts": posts},
    )


@parent_required
def create_comment(request, post_id=None, comment_id=None):
    if request.method == "POST":
        content = request.POST.get("content")
        if post_id:
            post = get_object_or_404(Post, id=post_id)
            new_comment = Comment.objects.create(
                content=content,
                post=post,
                type_of_comment=TypeOfComment.ORIGINAL,
            )
            new_comment.save()
            messages.success(request, f"You have replied to a post")

        elif comment_id:
            comment = get_object_or_404(Comment, id=comment_id)
            reply = Comment.objects.create(
                content=content,
                reply_to=comment,
                type_of_comment=TypeOfComment.REPLY,
            )
            reply.save()
            messages.success(request, f"You have replied to a post")

        else:
            messages.error(request, f"You don't have access to this page")

    return redirect("forum:post_detail")


def add_subscriber(request):
    if request.method == "POST":
        email = request.POST.get("email")
        # Check if a subscriber with the provided email already exists
        existing_subscriber = Subscriber.objects.filter(email=email).first()
        if existing_subscriber:
            messages.error(
                request, f"A subscriber with the email {email} already exists."
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
