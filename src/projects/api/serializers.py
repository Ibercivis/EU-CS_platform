from rest_framework import serializers
from django_countries.serializer_fields import CountryField
from PIL import Image
from projects.models import Project, Topic, Status, Keyword, FundingBody, OriginDatabase, CustomField
from projects.models import ParticipationTask, GeographicExtend, HasTag, DifficultyLevel, TranslatedProject
from projects.views import saveImageWithPath
from organisations.models import Organisation
from django.utils import timezone


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = '__all__'


class FundingBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = FundingBody
        fields = '__all__'


class OriginDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginDatabase
        fields = '__all__'


class CustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomField
        fields = '__all__'


class ParticipationTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipationTask
        fields = '__all__'


class GeographicExtendSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeographicExtend
        fields = '__all__'


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = 'id', 'name', 'url', 'country'


class HasTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HasTag
        fields = '__all__'


class DifficultyLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DifficultyLevel
        fields = '__all__'


class ProjectTranslateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslatedProject
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    topic = TopicSerializer(many=True, required=False)
    status = StatusSerializer(many=False)
    keywords = KeywordSerializer(many=True, required=False)
    fundingBody = FundingBodySerializer(many=True, required=False)
    originDatabase = OriginDatabaseSerializer(many=False, required=False)
    customField = CustomFieldSerializer(many=True, required=False)
    country = CountryField(required=False)
    start_date = serializers.DateTimeField(format="%Y-%m-%d", required=False)
    end_date = serializers.DateTimeField(format="%Y-%m-%d", required=False)
    mainOrganisation = OrganisationSerializer(many=False, required=False)
    organisation = OrganisationSerializer(many=True, required=False)
    hasTag = HasTagSerializer(many=True, required=False)
    participationTask = ParticipationTaskSerializer(many=True, required=False)
    geographicextend = GeographicExtendSerializer(many=True, required=False)
    difficultyLevel = DifficultyLevelSerializer(many=False, required=False)
    translatedProject = ProjectTranslateSerializer(many=True, required=False)

    class Meta:
        model = Project
        fields = '__all__'


class ProjectSerializerCreateUpdate(serializers.ModelSerializer):
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all())
    keywords = serializers.CharField(required=True)
    start_date = serializers.DateField(format="%Y-%m-%d", required=False)
    end_date = serializers.DateField(format="%Y-%m-%d", required=False)
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(), many=True)
    hasTag = serializers.PrimaryKeyRelatedField(queryset=HasTag.objects.all(), many=True, required=False)
    participationTask = serializers.PrimaryKeyRelatedField(
            queryset=ParticipationTask.objects.all(),
            many=True,
            required=False)
    difficultyLevel = serializers.PrimaryKeyRelatedField(
            queryset=DifficultyLevel.objects.all(),
            many=False,
            required=False)
    geographicextend = serializers.PrimaryKeyRelatedField(
            queryset=GeographicExtend.objects.all(),
            many=True,
            required=False)
    mainOrganisation = serializers.PrimaryKeyRelatedField(
            queryset=Organisation.objects.all(),
            many=False,
            required=False)
    organisation = serializers.PrimaryKeyRelatedField(
            queryset=Organisation.objects.all(),
            many=True,
            required=False)
    # TODO: fundingBody fundingBody = serializeddrs.
    fundingProgram = serializers.CharField(required=False)
    # TODO: originDatabase = serializers.CharField(required=False)

    class Meta:
        model = Project
        fields = [
                'id', 'name', 'url', 'aim', 'description', 'keywords', 'status', 'start_date', 'end_date', 'topic',
                'hasTag', 'participationTask', 'difficultyLevel', 'howToParticipate', 'equipment', 'geographicextend',
                'projectlocality', 'author', 'author_email', 'mainOrganisation', 'organisation', 'fundingProgram',
                'originURL', 'image1', 'image2', 'image3', 'projectGeographicLocation', 'dateCreated', 'dateUpdated'
                ]

    def updateKeywords(self):
        keywords = self.validated_data['keywords']
        finalKeywords = []
        for k in keywords.split(","):
            k = k.strip().capitalize()
            if not k.isdecimal():
                Keyword.objects.get_or_create(keyword=k)
                keyword_id = Keyword.objects.get(keyword=k).id
                finalKeywords.append(keyword_id)
        self.validated_data['keywords'] = finalKeywords

    def save(self, args, **kwargs):
        fundingBody = self.validated_data.get('fundingBody')
        self.validated_data['dateUpdated'] = timezone.now()
        self.updateKeywords()
        if(fundingBody):
            fundingBody, exist = FundingBody.objects.get_or_create(body=fundingBody)

        originDatabase = self.validated_data.get('originDatabase')
        if(originDatabase):
            originDatabase, exist = OriginDatabase.objects.get_or_create(originDatabase=originDatabase)

        image1 = self.validated_data.get('image1')
        print(self.validated_data)
        if(image1):
            photo = image1
            image = Image.open(photo)
            image_path = saveImageWithPath(image, photo.name)
            image1 = image_path

        image2 = self.validated_data.get('image2')
        if(image2):
            photo = image2
            image = Image.open(photo)
            image_path = saveImageWithPath(image, photo.name)
            image2 = image_path

        image3 = self.validated_data.get('image3')
        if(image3):
            photo = image3
            image = Image.open(photo)
            image_path = saveImageWithPath(image, photo.name)
            image3 = image_path

        moreItems = [('creator', args.user)]
        data = dict(list(self.validated_data.items()) + list(moreItems))
        self.instance = self.create(data)
        return "success"

    def update(self, instance, validated_data, requestData):
        self.updateKeywords()
        fundingBodySent = False
        originDatabaseSent = False
        mainOrganisationSent = False
        organisationSent = False
        image1Sent = False
        image2Sent = False
        image3Sent = False

        if 'fundingBody' in requestData:
            if requestData.get('fundingBody'):
                fundingBody = validated_data.pop('fundingBody')
                fundingBodySent = True
            else:
                instance.fundingBody = None
        if 'originDatabase' in requestData:
            if requestData.get('originDatabase'):
                originDatabase = validated_data.pop('originDatabase')
                originDatabaseSent = True
            else:
                instance.originDatabase = None

        if 'mainOrganisation' in requestData:
            if requestData.get('mainOrganisation'):
                mainOrganisation = validated_data.pop('mainOrganisation')
                mainOrganisationSent = True
            else:
                instance.mainOrganisation = None

        if 'organisation' in requestData:
            organisation = ""
            if requestData.get('organisation'):
                organisation = validated_data.pop('organisation')
            organisationSent = True

        if 'image1' in requestData:
            if requestData.get('image1'):
                image1 = validated_data.pop('image1')
            image1Sent = True

        if 'image2' in requestData:
            if requestData.get('image2'):
                image2 = validated_data.pop('image2')
            image2Sent = True

        if 'image3' in requestData:
            if requestData.get('image3'):
                image3 = validated_data.pop('image3')
            image3Sent = True

        super().update(instance, validated_data)

        if(fundingBodySent):
            fundingBody, exist = FundingBody.objects.get_or_create(body=fundingBody)
            instance.fundingBody = fundingBody

        if(originDatabaseSent):
            originDatabase, exist = OriginDatabase.objects.get_or_create(originDatabase=originDatabase)
            instance.originDatabase = originDatabase

        if(mainOrganisationSent):
            instance.mainOrganisation = mainOrganisation

        if(organisationSent):
            instance.organisation.set(organisation)

        if(image1Sent):
            if(image1):
                photo = image1
                image = Image.open(photo)
                image_path = saveImageWithPath(image, photo.name)
                instance.image1 = image_path

        if(image2Sent):
            if(image2):
                photo = image2
                image = Image.open(photo)
                image_path = saveImageWithPath(image, photo.name)
                instance.image2 = image_path

        if(image3Sent):
            if(image3):
                photo = image3
                image = Image.open(photo)
                image_path = saveImageWithPath(image, photo.name)
                instance.image3 = image_path
        instance.save()
        return instance


class ProjectTranslateCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TranslatedProject
        fields = [
                'translatedDescription', 'translatedAim', 'translatedHowToParticipate',
                'translatedEquipment', 'inLanguage']

    def save(self, args, pk):
        project = Project.objects.get(id=pk)
        moreItems = [('creator', args.user)]
        data = dict(list(self.validated_data.items()) + list(moreItems))
        self.instance = self.create(data)
        project.translatedProject.add(self.instance)
        print(self.instance)
        return self.instance.id
