# Generated by Django 3.2.23 on 2023-11-09 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0008_organisation_logocredit'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='description_de',
            field=models.CharField(max_length=3000, null=True),
        ),
        migrations.AddField(
            model_name='organisation',
            name='description_el',
            field=models.CharField(max_length=3000, null=True),
        ),
        migrations.AddField(
            model_name='organisation',
            name='description_en',
            field=models.CharField(max_length=3000, null=True),
        ),
        migrations.AddField(
            model_name='organisation',
            name='description_es',
            field=models.CharField(max_length=3000, null=True),
        ),
        migrations.AddField(
            model_name='organisation',
            name='description_et',
            field=models.CharField(max_length=3000, null=True),
        ),
        migrations.AddField(
            model_name='organisation',
            name='description_fr',
            field=models.CharField(max_length=3000, null=True),
        ),
        migrations.AddField(
            model_name='organisation',
            name='description_hu',
            field=models.CharField(max_length=3000, null=True),
        ),
        migrations.AddField(
            model_name='organisation',
            name='description_it',
            field=models.CharField(max_length=3000, null=True),
        ),
        migrations.AddField(
            model_name='organisation',
            name='description_lt',
            field=models.CharField(max_length=3000, null=True),
        ),
        migrations.AddField(
            model_name='organisation',
            name='description_nl',
            field=models.CharField(max_length=3000, null=True),
        ),
        migrations.AddField(
            model_name='organisation',
            name='description_pt',
            field=models.CharField(max_length=3000, null=True),
        ),
        migrations.AddField(
            model_name='organisation',
            name='description_sv',
            field=models.CharField(max_length=3000, null=True),
        ),
        migrations.AddField(
            model_name='organisationtype',
            name='type_de',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='organisationtype',
            name='type_el',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='organisationtype',
            name='type_en',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='organisationtype',
            name='type_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='organisationtype',
            name='type_et',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='organisationtype',
            name='type_fr',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='organisationtype',
            name='type_hu',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='organisationtype',
            name='type_it',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='organisationtype',
            name='type_lt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='organisationtype',
            name='type_nl',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='organisationtype',
            name='type_pt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='organisationtype',
            name='type_sv',
            field=models.TextField(null=True),
        ),
    ]
