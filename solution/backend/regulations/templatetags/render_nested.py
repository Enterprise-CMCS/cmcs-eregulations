from django.template import Library, TemplateDoesNotExist, loader

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
    except Exception:
        return value
