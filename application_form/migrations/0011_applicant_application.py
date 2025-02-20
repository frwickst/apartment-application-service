# Generated by Django 2.2.21 on 2021-05-24 08:59

import django.db.models.deletion
import enumfields.fields
import uuid
from django.db import migrations, models

import application_form.enums


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0002_profile"),
        ("application_form", "0010_remove_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="Application",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        verbose_name="application identifier",
                    ),
                ),
                (
                    "applicants_count",
                    models.PositiveSmallIntegerField(verbose_name="applicants count"),
                ),
                (
                    "type",
                    enumfields.fields.EnumField(
                        enum=application_form.enums.ApplicationType,
                        max_length=15,
                        verbose_name="application type",
                    ),
                ),
                (
                    "state",
                    enumfields.fields.EnumField(
                        default="submitted",
                        enum=application_form.enums.ApplicationState,
                        max_length=15,
                        verbose_name="application state",
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="users.Profile"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Applicant",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(max_length=30, verbose_name="first name"),
                ),
                (
                    "last_name",
                    models.CharField(max_length=150, verbose_name="last name"),
                ),
                ("email", models.EmailField(max_length=254, verbose_name="email")),
                (
                    "has_children",
                    models.BooleanField(default=False, verbose_name="has children"),
                ),
                ("age", models.PositiveSmallIntegerField(verbose_name="age")),
                (
                    "is_primary_applicant",
                    models.BooleanField(
                        default=False, verbose_name="is primary applicant"
                    ),
                ),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="application_form.Application",
                    ),
                ),
            ],
        ),
    ]
