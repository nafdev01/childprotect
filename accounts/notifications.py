# accounts/notifications.py
from django.template.loader import get_template
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib import messages
from django.utils import timezone


def send_parent_signup_confirm_email(request, parent, token_dict):
    try:
        device_info = {
            "browser_family": request.user_agent.browser.family,
            "browser_version": request.user_agent.browser.version_string,
            "device_os": request.user_agent.os.family,
            "device_version": request.user_agent.os.version_string,
        }

        # Merge the dictionaries using dictionary unpacking
        context_dict = {
            "parent": parent,
            "time": timezone.now(),
            "device_info": device_info,
            **token_dict,  # Merge token_dict into context_dict
        }

        # Retrieve entry by id
        subject = f"Please Confirm Your Email Address"
        sender = settings.EMAIL_HOST_USER
        recipient = parent.email
        message = get_template(
            "accounts/includes/parent_confirm_signup_email_template.html"
        ).render(context_dict)

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
    except Exception as e:
        # Handle any exceptions that might occur during email sending
        print(f"Error sending confirmation email: {str(e)}")
        return False


def send_parent_signup_confirmation_success_email(request, parent):
    device_info = {
        "browser_family": request.user_agent.browser.family,
        "browser_version": request.user_agent.browser.version_string,
        "device_os": request.user_agent.os.family,
        "device version": request.user_agent.os.version_string,
    }
    context_dict = {
        "parent": parent,
        "time": timezone.now(),
        "device_info": device_info,
    }
    # Retrieve entry by id
    subject = f"Email Confirmation Succcessful"
    sender = settings.EMAIL_HOST_USER
    recipient = parent.email
    message = get_template(
        "accounts/includes/parent_confirm_success_email_template.html"
    ).render(context_dict)
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


def send_child_signup_email(request, parent, child):
    device_info = {
        "browser_family": request.user_agent.browser.family,
        "browser_version": request.user_agent.browser.version_string,
        "device_os": request.user_agent.os.family,
        "device version": request.user_agent.os.version_string,
    }
    # Retrieve entry by id
    subject = f"Child {child.get_full_name()} Has Been Signed Up Successfully"
    sender = settings.EMAIL_HOST_USER
    recipient = parent.email
    message = get_template("accounts/includes/child_signup_email_template.html").render(
        {
            "parent": parent,
            "child": child,
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
    message = get_template("accounts/includes/parent_login_email_template.html").render(
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
    subject = f"Child {child.get_full_name()} Login Notification"
    sender = settings.EMAIL_HOST_USER
    recipient = parent.email
    message = get_template("accounts/includes/child_login_email_template.html").render(
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


def send_email_flagged_alert(request, flagged_words, search_phrase):
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
        return True
    else:
        messages.error(request, f"Email could not be sent to your parent")
        return False


def send_email_suspicious_alert(request, suspicious_results, search_phrase):
    child = request.user
    parent = child.childprofile.parent_profile.parent
    # Retrieve entry by id
    subject = f"Suspicious search by {child.get_full_name()}"
    sender = settings.EMAIL_HOST_USER
    recipient = parent.email
    message = get_template(
        "safesearch/includes/suspicious_search_email_template.html"
    ).render(
        {
            "child": child,
            "suspicious_results": suspicious_results,
            "search_phrase": search_phrase.phrase,
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
            request,
            f"Your search was flagged as suspicious and your parent has been alerted",
        )

    else:
        messages.error(request, f"Email could not be sent to your parent")


def send_email_newsletter_subscription(request, subscriber_email):
    subject = f"Thank You for Subscribing to Our Newsletter"
    sender = settings.EMAIL_HOST_USER
    recipient = subscriber_email
    message = get_template(
        "forum/includes/newsletter_subscription_email_template.html"
    ).render(
        {
            "subscriber_email": subscriber_email,
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
        messages.success(
            request, f"Subscriber with email {subscriber_email} has been added."
        )
    else:
        messages.error(request, f"Email could not be sent to subscriber")


def send_email_succesful_contact(
    request, name, email, contact_message, contact_subject
):
    subject = f"Thank You for Contacting Us"
    sender = settings.EMAIL_HOST_USER
    recipient = email
    message = get_template(
        "forum/includes/contact_successful_email_template.html"
    ).render(
        {
            "name": name,
            "subject": contact_subject,
            "message": contact_message,
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
        messages.success(
            request, f"Your contact details has been submitted successfully!"
        )
    else:
        messages.error(request, f"Contact details could not be sent to subscriber")


def send_parent_password_change_success_email(request, parent):
    context_dict = {
        "parent": parent,
    }
    # Retrieve entry by id
    subject = f"Password Change Succcessful"
    sender = settings.EMAIL_HOST_USER
    recipient = parent.email
    message = get_template(
        "accounts/includes/parent_password_change_email_template.html"
    ).render(context_dict)
    mail = EmailMessage(
        subject=subject,
        body=message,
        from_email=sender,
        to=[recipient],
        reply_to=[sender],
    )
    mail.content_subtype = "html"
    if mail.send():
        messages.success(request, "Your password was successfully updated!")
    else:
        messages.error(request, f"Password change error")
