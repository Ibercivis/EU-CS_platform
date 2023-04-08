# Generated by Django 2.2.28 on 2023-04-02 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0062_project_visits'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='visits',
            new_name='totalAccesses',
        ),
        migrations.RenameField(
            model_name='stats',
            old_name='views',
            new_name='accesses',
        ),
        migrations.RemoveField(
            model_name='project',
            name='stats',
        ),
        migrations.RemoveField(
            model_name='stats',
            name='day',
        ),
        migrations.AddField(
            model_name='stats',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.Project'),
        ),
    ]