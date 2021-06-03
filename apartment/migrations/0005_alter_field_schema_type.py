# Generated by Django 2.2.21 on 2021-06-04 07:55

import enumfields.fields
from django.db import migrations

import apartment.enums


class Migration(migrations.Migration):

    dependencies = [
        ("apartment", "0004_apartment_identifier_project"),
    ]

    operations = [
        migrations.AlterField(
            model_name="identifier",
            name="schema_type",
            field=enumfields.fields.EnumField(
                enum=apartment.enums.IdentifierSchemaType, max_length=10
            ),
        ),
    ]
