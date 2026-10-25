from django.core.mail import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken
from django.template.loader import render_to_string


def for_user(user):
    token = RefreshToken.for_user(user)

    return {
        "access": str(token.access_token),
        "refresh": str(token),
    }


def send_code(email, code):
    
    html_content = render_to_string(
    "authentication/email_templates.html",
    context={"code":code, "email":email},
    )
    
    message = EmailMessage(
        subject="EduMate verification code",
        body=html_content,
        to=[email],
    )
    message.content_subtype = "html"
    
    sent_count = message.send(using="default")
    
    if sent_count != 1:
        raise RuntimeError("Verification email was not accepted by the mail backend.")
    return sent_count
