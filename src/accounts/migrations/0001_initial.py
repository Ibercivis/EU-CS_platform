# Generated by Django 2.2.13 on 2021-05-12 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ecsa_fee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('membership', models.TextField()),
                ('amount', models.IntegerField()),
            ],
        ),
    ]