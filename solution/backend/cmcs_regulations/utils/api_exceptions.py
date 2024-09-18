from rest_framework import serializers
from rest_framework.exceptions import APIException


class ExceptionSerializer(serializers.Serializer):
    detail = serializers.CharField()
    text = serializers.CharField()
    non_field_errors = serializers.ListField(child=serializers.CharField())


class BadRequest(APIException):
    status_code = 400
    default_detail = "Bad Request."
    default_code = "bad_request"
