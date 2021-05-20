# Generated by Django 2.2.13 on 2021-04-09 11:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0006_auto_20210311_1231'),
        ('profiles', '0011_auto_20210323_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='city',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='City'),
        ),
        migrations.AddField(
            model_name='profile',
            name='country',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Country'),
        ),
        migrations.AddField(
            model_name='profile',
            name='ecsa_billing_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='ecsa_reduced_fee',
            field=models.BooleanField(default=False, verbose_name='Reduced fee'),
        ),
        migrations.AddField(
            model_name='profile',
            name='lastname',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Last name'),
        ),
        migrations.AddField(
            model_name='profile',
            name='occupation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organisations.OrganisationType'),
        ),
        migrations.AddField(
            model_name='profile',
            name='postal_code',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='street',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Street'),
        ),
    ]