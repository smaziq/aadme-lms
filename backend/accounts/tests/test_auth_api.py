import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api():
    return APIClient()


@pytest.mark.django_db
def test_login_returns_token(api):
    User.objects.create_user(email="admin@example.com", password="secret123", role="admin")
    res = api.post("/api/auth/login/", {"email": "admin@example.com", "password": "secret123"}, format="json")
    assert res.status_code == 200
    assert "token" in res.data
    assert res.data["user"]["role"] == "admin"


@pytest.mark.django_db
def test_me_requires_auth(api):
    res = api.get("/api/auth/me/")
    assert res.status_code == 401


@pytest.mark.django_db
def test_me_returns_user(api):
    user = User.objects.create_user(email="admin@example.com", password="secret123", role="admin")
    token = Token.objects.create(user=user)
    api.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    res = api.get("/api/auth/me/")
    assert res.status_code == 200
    assert res.data["email"] == "admin@example.com"