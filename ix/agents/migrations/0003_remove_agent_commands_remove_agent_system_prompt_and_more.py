# Generated by Django 4.2 on 2023-05-04 01:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("chains", "0001_initial"),
        ("agents", "0002_agent_agent_class_path"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="agent",
            name="commands",
        ),
        migrations.RemoveField(
            model_name="agent",
            name="system_prompt",
        ),
        migrations.AddField(
            model_name="agent",
            name="chain",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="chains.chain",
            ),
        ),
    ]
