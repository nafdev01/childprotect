from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.notifications import send_email_newsletter_subscription
from .models import Post, Comment, TypeOfComment, Subscriber
from django.contrib.auth.decorators import login_required


@login_required
def post_detail(request):
    posts = Post.objects.all()

    return render(
        request,
        "forum/forum.html",
        {"posts": posts},
    )


@login_required
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
        subscriber_email = request.POST.get("email")
        # Check if a subscriber with the provided email already exists
        existing_subscriber = Subscriber.objects.filter(email=subscriber_email).first()
        if existing_subscriber:
            messages.error(
                request, f"A subscriber with the email {subscriber_email} already exists."
            )
        else:
            subscriber = Subscriber.objects.create(email=subscriber_email)
            subscriber.save()
            send_email_newsletter_subscription(request, subscriber_email)
    else:
        messages.error(request, f"You cannot access this page")

    return redirect("home")
