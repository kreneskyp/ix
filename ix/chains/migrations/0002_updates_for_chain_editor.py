# Generated by Django 4.2.1 on 2023-06-03 19:26

from django.db import migrations, models
import django.db.models.deletion
import ix.chains.models


class Migration(migrations.Migration):
    dependencies = [
        ("chains", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChainNodeType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(null=True)),
                ("class_path", models.CharField(max_length=255)),
                ("type", models.CharField(max_length=255)),
                (
                    "display_type",
                    models.CharField(
                        choices=[("node", "node"), ("list", "list"), ("map", "map")],
                        default="node",
                        max_length=10,
                    ),
                ),
                ("config", models.JSONField(null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name="chainnode",
            name="node_type",
        ),
        migrations.AddField(
            model_name="chainedge",
            name="chain",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="edges",
                to="chains.chain",
            ),
        ),
        migrations.AddField(
            model_name="chainnode",
            name="chain",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="nodes",
                to="chains.chain",
            ),
        ),
        migrations.AddField(
            model_name="chainnode",
            name="position",
            field=models.JSONField(default=ix.chains.models.default_position),
        ),
    ]
