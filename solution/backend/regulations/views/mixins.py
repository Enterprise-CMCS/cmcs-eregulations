from django.shortcuts import redirect
from django.urls import reverse


def build_citation(context):
    citation = []
    if 'part' in context:
        citation.append(context["part"])
        if 'section' in context:
            citation.append(context["section"])
        elif 'subpart' in context:
            citation.append(context["subpart"])
    return citation


class CitationContextMixin:
    def get_context_data(self, **kwargs):
        context = super(CitationContextMixin, self).get_context_data(**kwargs)
        context['citation'] = build_citation(context)
        return context


class IsAuthenticatedMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:

            redirect_string = '?' + request.GET.urlencode() if request.GET else ''
            return redirect('/login' + '?next=%s' % request.path + redirect_string)

        return super().dispatch(request, *args, **kwargs)
