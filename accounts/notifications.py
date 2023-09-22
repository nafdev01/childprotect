# accounts/notifications.py
from django.template.loader import get_template
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib import messages
from django.utils import timezone


def send_parent_login_email(request):
    parent = request.user
    device_info = {
        "browser_family": request.user_agent.browser.family,
        "browser_version": request.user_agent.browser.version_string,
        "device_os": request.user_agent.os.family,
        "device version": request.user_agent.os.version_string,
    }
    # Retrieve entry by id
    subject = f"Successful Login Notification"
    sender = settings.EMAIL_HOST_USER
    recipient = parent.email
    message = get_template("safesearch/includes/parent_login_email_template.html").render(
        {
            "parent": parent,
            "time": timezone.now(),
            "device_info": device_info,
        }
    )
    mail = EmailMessage(
        subject=subject,
        body=message,
        from_email=sender,
        to=[recipient],
        reply_to=[sender],
    )
    mail.content_subtype = "html"
    if mail.send():
        return True
    else:
        return False


def send_child_login_email(request):
    child = request.user
    parent = child.childprofile.parent_profile.parent
    device_info = {
        "browser_family": request.user_agent.browser.family,
        "browser_version": request.user_agent.browser.version_string,
        "device_os": request.user_agent.os.family,
        "device version": request.user_agent.os.version_string,
    }
    # Retrieve entry by id
    subject = f"Successful Login Notification"
    sender = settings.EMAIL_HOST_USER
    recipient = parent.email
    message = get_template("safesearch/includes/child_login_email_template.html").render(
        {
            "child": child,
            "parent": parent,
            "time": timezone.now(),
            "device_info": device_info,
        }
    )
    mail = EmailMessage(
        subject=subject,
        body=message,
        from_email=sender,
        to=[recipient],
        reply_to=[sender],
    )
    mail.content_subtype = "html"
    if mail.send():
        return True
    else:
        return False



def send_email_alert(request, flagged_words, search_phrase):
    child = request.user
    parent = child.childprofile.parent_profile.parent
    # Retrieve entry by id
    subject = f"A search by your child {child.get_full_name()} has been flagged"
    sender = settings.EMAIL_HOST_USER
    recipient = parent.email
    message = get_template(
        "safesearch/includes/flagged_search_email_template.html"
    ).render(
        {
            "child": child,
            "flagged_words": flagged_words,
            "search_phrase": search_phrase.phrase.split(),
        }
    )
    mail = EmailMessage(
        subject=subject,
        body=message,
        from_email=sender,
        to=[recipient],
        reply_to=[sender],
    )
    mail.content_subtype = "html"
    if mail.send():
        messages.warning(
            request, f"Your parent has been alerted about your illegal search"
        )
    else:
        messages.error(request, f"Email could not be sent to your parent")