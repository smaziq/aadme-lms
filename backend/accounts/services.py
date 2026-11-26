from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import InviteToken

INVITE_TTL_HOURS = 72


def create_and_send_invite(user) -> InviteToken:
    InviteToken.objects.filter(user=user, used_at__isnull=True).delete()
    invite = InviteToken.objects.create(
        user=user,
        token=InviteToken.generate_token(),
        expires_at=timezone.now() + timedelta(hours=INVITE_TTL_HOURS),
    )
    link = f"{settings.FRONTEND_BASE_URL}/set-password?token={invite.token}"
    send_mail(
        subject="Set your AADME Learning password",
        message=f"Welcome. Set your password: {link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return invite