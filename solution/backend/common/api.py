from drf_spectacular.utils import OpenApiParameter


def OpenApiQueryParameter(name, description, type, required):
    return OpenApiParameter(name=name, description=description, required=required, type=type, location=OpenApiParameter.QUERY)
