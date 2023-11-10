from modeltranslation.translator import translator, TranslationOptions, register
from .models import Audience, Category, EducationLevel, LearningResourceType,  Resource, Theme

@register(Audience)
class AudienceTranslationOptions(TranslationOptions):
    fields = ('audience',)

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('text',)

@register(EducationLevel)
class EducationLevelTranslationOptions(TranslationOptions):
    fields = ('educationLevel',)

@register(LearningResourceType)
class LearningResourceTypeTranslationOptions(TranslationOptions):
    fields = ('learningResourceType',)

@register(Resource)
class ResourceTranslationOptions(TranslationOptions):
    fields = ('name', 'abstract', 'description_citizen_science_aspects')

@register(Theme)
class ThemeTranslationOptions(TranslationOptions):
    fields = ('theme',) 
