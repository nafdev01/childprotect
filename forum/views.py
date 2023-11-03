from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.notifications import (
    send_email_newsletter_subscription,
    send_email_succesful_contact,
)
from .models import Post, Comment, TypeOfComment, Subscriber, Contact
from accounts.decorators import parent_required, child_required


@parent_required
def post_list(request):
    posts = Post.objects.all()
    parent = request.user
    parent_profile = parent.parentprofile

    template_name = "forum/forum.html"
    context = {"posts": posts, "parent": parent, "parent_profile": parent_profile}

    return render(request, template_name=template_name, context=context)


@parent_required
def post_detail(request, post_slug, parent_id):
    parent = request.user
    parent_profile = parent.parentprofile

    post = get_object_or_404(Post, slug=post_slug, created_by_id=parent_id)
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
def create_comment(request, post_id=None, comment_id=None):
    if request.method == "POST":
        content = request.POST.get("content")
        if post_id:
            post = get_object_or_404(Post, id=post_id)
            new_comment = Comment.objects.create(
                content=content,
                post=post,
                type_of_comment=TypeOfComment.ORIGINAL,
                comment_by=request.user,
            )
            new_comment.save()
            messages.success(request, f"You have replied to a post")

        elif comment_id:
            comment = get_object_or_404(Comment, id=comment_id)
            post = comment.post
            reply = Comment.objects.create(
                content=content,
                reply_to=comment,
                type_of_comment=TypeOfComment.REPLY,
                comment_by=request.user,
            )
            reply.save()
            messages.success(request, f"You have replied to a post")

        else:
            messages.error(request, f"You don't have access to this page")
            return redirect("forum:post_list")

    return redirect(post)


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


# chatpage view
def chatPage(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login-user")
    context = {}
    return render(request, "forum/chatPage.html", context)
