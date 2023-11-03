import markdown
from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe

from forum.models import Comment, Post

register = template.Library()


@register.filter(name="markdown")
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
