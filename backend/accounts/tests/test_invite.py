import pytest
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import InviteToken
from accounts.services import create_and_send_invite

User = get_user_model()


@pytest.mark.django_db
def test_create_and_send_invite_sends_email(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    user = User.objects.create_user(email="s@example.com", password=None, role="student")
    user.set_unusable_password()
    user.save()
    invite = create_and_send_invite(user)
    assert invite.token
    assert len(mail.outbox) == 1
    assert invite.token in mail.outbox[0].body


@pytest.mark.django_db
def test_set_password_with_valid_token():
    user = User.objects.create_user(email="s@example.com", password=None, role="student")
    user.set_unusable_password()
    user.save()
    invite = create_and_send_invite(user)
    api = APIClient()
    res = api.post(
        "/api/auth/set-password/",
        {"token": invite.token, "password": "newpass123"},
        format="json",
    )
    assert res.status_code == 200
    assert "token" in res.data
    user.refresh_from_db()
    assert user.check_password("newpass123")
    invite.refresh_from_db()
    assert invite.used_at is not None


@pytest.mark.django_db
def test_set_password_rejects_used_token():
    user = User.objects.create_user(email="s@example.com", password=None, role="student")
    user.set_unusable_password()
    user.save()
    invite = create_and_send_invite(user)
    invite.mark_used()
    api = APIClient()
    res = api.post(
        "/api/auth/set-password/",
        {"token": invite.token, "password": "newpass123"},
        format="json",
    )
    assert res.status_code == 400
    assert "already been used" in str(res.data).lower()


@pytest.mark.django_db
def test_set_password_rejects_expired_token():
    user = User.objects.create_user(email="s@example.com", password=None, role="student")
    invite = InviteToken.objects.create(
        user=user,
        token="deadbeef",
        expires_at=timezone.now() - timedelta(hours=1),
    )
    api = APIClient()
    res = api.post(
        "/api/auth/set-password/",
        {"token": "deadbeef", "password": "newpass123"},
        format="json",
    )
    assert res.status_code == 400