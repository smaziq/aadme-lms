import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_create_user_with_role():
    user = User.objects.create_user(
        email="student@example.com",
        password="secret123",
        role=User.Role.STUDENT,
    )
    assert user.email == "student@example.com"
    assert user.role == "student"
    assert user.check_password("secret123")

@pytest.mark.django_db
def test_email_is_username():
    user = User.objects.create_user(
        email="admin@example.com",
        password="secret123",
        role="admin",
    )
    assert user.get_username() == "admin@example.com"