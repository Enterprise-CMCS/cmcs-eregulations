from datetime import date

from rest_framework import generics, serializers
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.postgres.aggregates import StringAgg
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

from regcore.models import Part, ParserConfiguration

from regcore.search.models import Synonym

from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import authentication
from rest_framework import exceptions

# TODO: replace with v3views.py after v3 move


class SettingsUser:  # TODO: keep this on v3 move
    is_authenticated = False


class SettingsAuthentication(authentication.BasicAuthentication):  # TODO: keep this on v3 move
    def authenticate_credentials(self, userid, password, request=None):
        if userid == settings.HTTP_AUTH_USER and password == settings.HTTP_AUTH_PASSWORD:
            user = SettingsUser()
            user.is_authenticated = True
            return (user, None)
        raise exceptions.AuthenticationFailed('No such user')


class ListPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = "__all__"
        extra_kwargs = {
            'document': {'write_only': True}
        }


class ExistingPartSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            'date': instance.get("date"),
            'partName': instance.get("partName").split(","),
        }


class PartListView(generics.ListAPIView):
    serializer_class = ListPartSerializer

    def get_queryset(self):
        return Part.objects.filter(date__lte=date.today()).distinct("title", "name").order_by("title", "name")


class PartsView(generics.ListCreateAPIView):
    serializer_class = ListPartSerializer
    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        query = Part.objects.all()
        part = self.kwargs.get("name")
        title = self.kwargs.get("title")
        if part and title:
            query = query.filter(name=part).filter(title=title).order_by('-date')
        return query

    def create(self, request, *args, **kwargs):
        query = Part.objects.filter(
            name=request.data.get("name"),
            title=request.data.get("title"),
            date=request.data.get("date"),
        )
        if query.exists():
            serializer = self.get_serializer(query.get(), data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        return super().create(request, *args, **kwargs)


class ListEffectivePartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Part
        fields = ("id", "name", "title", "date", "last_updated", "structure")


class EffectiveTitlesView(generics.ListAPIView):
    serializer_class = ListEffectivePartSerializer

    def get_queryset(self):
        date = self.kwargs.get("date")
        return Part.objects.filter(date__lte=date).order_by("name", "-date").distinct("name")


class EffectivePartsView(generics.ListAPIView):
    serializer_class = ListEffectivePartSerializer

    def get_queryset(self):
        title = self.kwargs.get("title")
        date = self.kwargs.get("date")
        return Part.objects.filter(title=title).filter(date__lte=date).order_by("name", "-date").distinct("name")


class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ("id", "name", "title", "date", "last_updated", "document", "structure", "toc")


class EffectivePartView(generics.RetrieveAPIView):
    authentication_classes = [SettingsAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    serializer_class = PartSerializer
    lookup_field = "name"

    def get_queryset(self):
        title = self.kwargs.get("title")
        date = self.kwargs.get("date")
        return Part.objects.filter(title=title).filter(date__lte=date)

    def get_object(self):
        return self.get_queryset().filter(name=self.kwargs.get(self.lookup_field)).latest("date")


class ExistingPartsView(generics.ListAPIView):

    serializer_class = ExistingPartSerializer

    def get_queryset(self):
        title = self.kwargs.get("title")
        return Part.objects.filter(title=title).values('date').annotate(
            partName=StringAgg('name', delimiter=','),
        )


class ListEffectivePartTocSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ("id", "name", "title", "date", "last_updated", "toc")


class EffectivePartTocView(EffectivePartView):
    serializer_class = ListEffectivePartTocSerializer


class TitleConfigurationSerializer(serializers.Serializer):
    title = serializers.IntegerField()
    subchapters = serializers.CharField()
    parts = serializers.CharField()


class ParserConfigurationSerializer(serializers.ModelSerializer):
    titles = TitleConfigurationSerializer(many=True)

    class Meta:
        model = ParserConfiguration
        fields = (
            "workers",
            "attempts",
            "loglevel",
            "upload_supplemental_locations",
            "log_parse_errors",
            "skip_versions",
            "titles",
        )


class ParserConfigurationView(generics.RetrieveAPIView):
    serializer_class = ParserConfigurationSerializer

    def get_object(self):
        return ParserConfiguration.objects.all()[0]


def process_body(raw_synonyms):
    new_synonyms = []
    existing_synonyms = []
    for line in raw_synonyms:
        related_words = []
        for syn in line.split(","):
            new_syn, created = Synonym.objects.get_or_create(isActive=True, baseWord=syn.strip())
            if created:
                new_synonyms.append(syn)
            else:
                existing_synonyms.append(syn)
            for word in related_words:
                new_syn.synonyms.add(word)
            related_words.append(new_syn)

    return new_synonyms, existing_synonyms


class BulkSynonymView(PermissionRequiredMixin, View):
    permission_required = 'search.add_synonym'

    def get(self, request):

        return render(request, 'add_synonym.html', {})

    def post(self, request):

        raw_synonyms = request.POST['raw_synonyms'].split("\r\n")
        new_synonyms, existing_synonyms = process_body(raw_synonyms)

        if len(new_synonyms):
            messages.add_message(request, messages.INFO, "The following synonyms have been added: " + ", ".join(new_synonyms))
        if len(existing_synonyms):
            messages.add_message(request, messages.WARNING, "The following synonyms have not been added because they already exist: " + ", ".join(existing_synonyms))
        return redirect("admin/search/synonym/")

