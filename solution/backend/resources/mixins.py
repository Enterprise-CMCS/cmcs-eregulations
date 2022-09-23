
from django.http import HttpResponse
from django.core import serializers


class ExportJSONMixin:
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
