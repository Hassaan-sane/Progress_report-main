# Generated by Django 5.1.2 on 2024-10-24 11:50

import django.db.models.deletion
from django.db import migrations, models



class Migration(migrations.Migration):
    dependencies = [
        ("emp_rprt", "0010_progress_workflow_stage_workflowstage_order_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="progressupdated",
            name="workflow_stage",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="emp_rprt.workflowstage",
            ),
        ),
    ]
