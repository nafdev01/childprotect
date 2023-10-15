from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Post, Comment, TypeOfComment
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
