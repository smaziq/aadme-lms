import pytest
from catalog.models import Program, Module, Lesson, Batch


@pytest.mark.django_db
def test_program_module_lesson_ordering():
    program = Program.objects.create(title="Agentic AI", slug="agentic-ai", is_published=True)
    m1 = Module.objects.create(program=program, title="Week 1", order=1)
    lesson = Lesson.objects.create(
        module=m1,
        title="Intro",
        order=1,
        body="Hello",
        links=[{"label": "Docs", "url": "https://example.com"}],
        is_published=True,
    )
    assert list(program.modules.values_list("title", flat=True)) == ["Week 1"]
    assert lesson.module_id == m1.id


@pytest.mark.django_db
def test_batch_belongs_to_program():
    program = Program.objects.create(title="P", slug="p")
    batch = Batch.objects.create(program=program, name="Jan 2027")
    assert batch.program_id == program.id