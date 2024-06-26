# Generated by Django 2.2.28 on 2023-04-07 19:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0066_remove_likes_day'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='firstAccess',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='First access'),
        ),
        migrations.AlterField(
            model_name='likes',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='projects.Project'),
        ),
    ]
