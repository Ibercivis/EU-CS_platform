# Generated by Django 2.2.13 on 2022-09-12 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0045_auto_20211026_0141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='authors',
            field=models.ManyToManyField(blank=True, to='authors.Author'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='educationLevel',
            field=models.ManyToManyField(blank=True, to='resources.EducationLevel'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='featured',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='resource',
            name='inLanguage',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='resource',
            name='learningResourceType',
            field=models.ManyToManyField(blank=True, to='resources.LearningResourceType'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='organisation',
            field=models.ManyToManyField(blank=True, to='organisations.Organisation'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='project',
            field=models.ManyToManyField(blank=True, to='projects.Project'),
        ),
    ]
