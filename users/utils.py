from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import email_verification_token


def send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verify_url = f"{settings.FRONTEND_URL}/verify-email?uid={uid}&token={token}"
    resend_url = f"{settings.FRONTEND_URL}/resend-verification?email={user.email}"

    context = {
        "username": user.username,
        "verify_url": verify_url,
        "resend_url": resend_url,
        "expiry_hours": 0.1,
    }

    subject = "Verify your email"
    text_body = render_to_string("emails/verify_email.txt", context)
    html_body = render_to_string("emails/verify_email.html", context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)