# Generated by Django 3.2.23 on 2023-11-08 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0085_auto_20231108_0027'),
    ]

    operations = [
        migrations.AddField(
            model_name='participationtask',
            name='participationTask_de',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='participationtask',
            name='participationTask_el',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='participationtask',
            name='participationTask_en',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='participationtask',
            name='participationTask_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='participationtask',
            name='participationTask_et',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='participationtask',
            name='participationTask_fr',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='participationtask',
            name='participationTask_hu',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='participationtask',
            name='participationTask_it',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='participationtask',
            name='participationTask_lt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='participationtask',
            name='participationTask_nl',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='participationtask',
            name='participationTask_pt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='participationtask',
            name='participationTask_sv',
            field=models.TextField(null=True),
        ),
    ]
