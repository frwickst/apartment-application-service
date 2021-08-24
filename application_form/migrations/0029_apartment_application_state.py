# Generated by Django 2.2.24 on 2021-08-24 12:48

import enumfields.fields
from django.db import migrations

import application_form.enums


class Migration(migrations.Migration):

    dependencies = [
        ("application_form", "0028_reservation_queue"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="application",
            name="state",
        ),
        migrations.AddField(
            model_name="applicationapartment",
            name="state",
            field=enumfields.fields.EnumField(
                default="submitted",
                enum=application_form.enums.ApplicationState,
                max_length=15,
                verbose_name="application state",
            ),
        ),
    ]
