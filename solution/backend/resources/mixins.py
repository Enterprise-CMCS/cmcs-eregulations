import csv
from django.http import HttpResponse
from django.db.models.constants import LOOKUP_SEP
from django.core import serializers


class ExportCsvMixin:
    def export_as_csv(self, request, queryset, related_models=[]):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names + related_models)
        for obj in queryset:
            fields = [getattr(obj, field) for field in field_names]
            related_fields = [
                '|'.join([str(rf.id) for rf in getattr(obj, related_model).all()])
                for related_model in related_models
            ]
            writer.writerow(fields + related_fields)

        return response

    export_as_csv.short_description = "Export Selected"

    def export_all_as_csv(self, request):
        related_models = [many_to_many.name for many_to_many in self.model._meta.many_to_many]
        if len(related_models):
            queryset = self.model.objects.all().prefetch_related(LOOKUP_SEP.join(related_models))
        else:
            queryset = self.model.objects.all()
        return self.export_as_csv(request, queryset, related_models)

    def export_all_as_json(self, request):

        format = "json"
        indent = 2

        model = self.model
        pk_list = model.objects.values_list('pk', flat=True)
        queryset = model.objects.all()
        objects = list(queryset)
        parents = []
        if len(objects[0].__class__.__bases__):
            base = objects[0].__class__.__bases__[0]
            # Model is the top level class that everything derives from
            while base.__name__ != 'Model':
                print(base.__class__.__name__)
                r = list(base.objects.filter(pk__in=pk_list))
                base = r[0].__class__.__bases__[0]
                parents = r + parents

        parents.extend(objects)
        stream = serializers.serialize(format, parents, indent=indent)
        response = HttpResponse(stream, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.json'.format(model._meta)
        return response
