# Generated by Django 3.2.23 on 2023-11-09 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eucitizensciencetheme', '0013_auto_20231109_2258'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='homesection',
            options={'ordering': ['position'], 'verbose_name_plural': 'HomeSection'},
        ),
        migrations.AddField(
            model_name='homesection',
            name='position',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
