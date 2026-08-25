from drf_spectacular.utils import OpenApiParameter


def OpenApiPathParameter(name, description, type):
    return OpenApiParameter(name=name, description=description, required=True, type=type, location=OpenApiParameter.PATH)
