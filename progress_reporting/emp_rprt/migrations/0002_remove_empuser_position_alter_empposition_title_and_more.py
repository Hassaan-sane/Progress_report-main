# Generated by Django 5.1.2 on 2024-10-23 06:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("emp_rprt", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="empuser",
            name="position",
        ),
        migrations.AlterField(
            model_name="empposition",
            name="title",
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name="products",
            name="sku",
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name="workdetail",
            name="title",
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.CreateModel(
            name="ProgressUpdated",
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
                ("date_changed", models.DateField(auto_now_add=True)),
                (
                    "status_changed_to",
                    models.CharField(
                        choices=[("ongoing", "Ongoing"), ("completed", "Completed")],
                        max_length=20,
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="emp_rprt.products",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="emp_rprt.empuser",
                    ),
                ),
                (
                    "work",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="emp_rprt.workdetail",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserPosition",
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
                (
                    "position",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="emp_rprt.empposition",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="emp_rprt.empuser",
                    ),
                ),
                (
                    "work",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="emp_rprt.workdetail",
                    ),
                ),
            ],
        ),
    ]
