from django.template import Library, loader, TemplateDoesNotExist

register = Library()


@register.simple_tag()
def render_nested(*templates, context=None, **kwargs):
    if context is None:
        context = {}
    try:
        return loader.select_template(templates).render({**context, **kwargs})
    except TemplateDoesNotExist:
        pass


@register.filter
def interpolate(value, arg):
    try:
        return value.format(**arg)
    except:
        return value
