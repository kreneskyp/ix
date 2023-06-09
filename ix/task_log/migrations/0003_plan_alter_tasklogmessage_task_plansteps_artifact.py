# Generated by Django 4.2 on 2023-05-02 14:10

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("task_log", "0002_tasklogmessage_parent"),
    ]

    operations = [
        migrations.CreateModel(
            name="Plan",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_draft", models.BooleanField(default=True)),
                ("is_complete", models.BooleanField(default=False)),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_plans",
                        to="task_log.task",
                    ),
                ),
                (
                    "runner",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ran_plans",
                        to="task_log.task",
                    ),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="tasklogmessage",
            name="task",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="messages",
                to="task_log.task",
            ),
        ),
        migrations.CreateModel(
            name="PlanSteps",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("is_complete", models.BooleanField(default=False)),
                ("details", models.JSONField()),
                (
                    "plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="steps",
                        to="task_log.plan",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Artifact",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("key", models.CharField(max_length=128)),
                ("artifact_type", models.CharField(max_length=128)),
                ("name", models.CharField(max_length=128)),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("reference", models.JSONField()),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="artifacts",
                        to="task_log.task",
                    ),
                ),
            ],
        ),
    ]
