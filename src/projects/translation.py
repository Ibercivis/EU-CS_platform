from modeltranslation.translator import translator, TranslationOptions,register
from .models import Topic, Status, HasTag, DifficultyLevel, ParticipationTask, Project

@register(DifficultyLevel)
class DifficultyLevelTranslationOptions(TranslationOptions):
    fields = ('difficultyLevel',)

@register(HasTag)
class HasTagTranslationOptions(TranslationOptions):
    fields = ('hasTag',)

@register(ParticipationTask)
class ParticipationTaskTranslationOptions(TranslationOptions):
    fields = ('participationTask',)

@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('description', 'aim', 'howToParticipate', 'equipment', )

@register(Status)
class StatusTranslationOptions(TranslationOptions):
    fields = ('status',)

@register(Topic)
class TopicTranslationOptions(TranslationOptions):
    fields = ('topic',)






