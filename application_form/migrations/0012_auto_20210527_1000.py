# Generated by Django 2.2.21 on 2021-05-27 07:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apartment", "0002_auto_20210526_1910"),
        ("application_form", "0011_applicant_application"),
    ]

    operations = [
        migrations.AlterField(
            model_name="applicant",
            name="application",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="applicants",
                to="application_form.Application",
            ),
        ),
        migrations.CreateModel(
            name="ApplicationApartment",
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
                    "priority_number",
                    models.PositiveSmallIntegerField(verbose_name="priority number"),
                ),
                (
                    "apartment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="apartment.Apartment",
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
        migrations.AddField(
            model_name="application",
            name="apartments",
            field=models.ManyToManyField(
                through="application_form.ApplicationApartment",
                to="apartment.Apartment",
            ),
        ),
    ]
