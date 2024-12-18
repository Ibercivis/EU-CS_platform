# Generated by Django 3.2.23 on 2024-04-12 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0057_auto_20240327_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='audience',
            name='audience_de',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='audience',
            name='audience_el',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='audience',
            name='audience_et',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='audience',
            name='audience_fr',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='audience',
            name='audience_hu',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='audience',
            name='audience_it',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='audience',
            name='audience_lt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='audience',
            name='audience_nl',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='audience',
            name='audience_sv',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='text_de',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='text_el',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='text_et',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='text_fr',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='text_hu',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='text_it',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='text_lt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='text_nl',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='text_sv',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='educationlevel',
            name='educationLevel_de',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='educationlevel',
            name='educationLevel_el',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='educationlevel',
            name='educationLevel_et',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='educationlevel',
            name='educationLevel_fr',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='educationlevel',
            name='educationLevel_hu',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='educationlevel',
            name='educationLevel_it',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='educationlevel',
            name='educationLevel_lt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='educationlevel',
            name='educationLevel_nl',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='educationlevel',
            name='educationLevel_sv',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='paragraph_de',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='paragraph_el',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='paragraph_et',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='paragraph_fr',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='paragraph_hu',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='paragraph_it',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='paragraph_lt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='paragraph_nl',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='paragraph_sv',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='title_de',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='title_el',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='title_et',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='title_fr',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='title_hu',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='title_it',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='title_lt',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='title_nl',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='helptext',
            name='title_sv',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='learningresourcetype',
            name='learningResourceType_de',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='learningresourcetype',
            name='learningResourceType_el',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='learningresourcetype',
            name='learningResourceType_et',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='learningresourcetype',
            name='learningResourceType_fr',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='learningresourcetype',
            name='learningResourceType_hu',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='learningresourcetype',
            name='learningResourceType_it',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='learningresourcetype',
            name='learningResourceType_lt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='learningresourcetype',
            name='learningResourceType_nl',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='learningresourcetype',
            name='learningResourceType_sv',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='abstract_de',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='abstract_el',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='abstract_et',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='abstract_fr',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='abstract_hu',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='abstract_it',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='abstract_lt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='abstract_nl',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='abstract_sv',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='description_citizen_science_aspects_de',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='description_citizen_science_aspects_el',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='description_citizen_science_aspects_et',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='description_citizen_science_aspects_fr',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='description_citizen_science_aspects_hu',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='description_citizen_science_aspects_it',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='description_citizen_science_aspects_lt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='description_citizen_science_aspects_nl',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='description_citizen_science_aspects_sv',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='name_de',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='name_el',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='name_et',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='name_fr',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='name_hu',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='name_it',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='name_lt',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='name_nl',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='name_sv',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='theme',
            name='theme_de',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='theme',
            name='theme_el',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='theme',
            name='theme_et',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='theme',
            name='theme_fr',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='theme',
            name='theme_hu',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='theme',
            name='theme_it',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='theme',
            name='theme_lt',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='theme',
            name='theme_nl',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='theme',
            name='theme_sv',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
