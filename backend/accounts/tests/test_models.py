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


from accounts.models import Student


@pytest.mark.django_db
def test_student_linked_to_user():
    user = User.objects.create_user(
        email="s1@example.com", password="x", role=User.Role.STUDENT
    )
    student = Student.objects.create(user=user, full_name="Ada Lovelace")
    assert student.user_id == user.id
    assert student.crm_person_id is None


@pytest.mark.django_db
def test_crm_person_id_unique_when_set():
    u1 = User.objects.create_user(email="a@example.com", password="x", role="student")
    u2 = User.objects.create_user(email="b@example.com", password="x", role="student")
    Student.objects.create(user=u1, full_name="A", crm_person_id="crm-1")
    with pytest.raises(Exception):
        Student.objects.create(user=u2, full_name="B", crm_person_id="crm-1")