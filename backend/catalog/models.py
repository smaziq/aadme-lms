from django.db import models


class Program(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Module(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    body = models.TextField(blank=True)
    links = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["order", "id"]


class Batch(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="batches")
    name = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.program.slug}:{self.name}"