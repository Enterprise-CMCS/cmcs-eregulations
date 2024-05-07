from django.db import models

from common.mixins import DisplayNameFieldMixin


class NewAbstractCategory(models.Model, DisplayNameFieldMixin):
    pass


class PublicCategory(NewAbstractCategory):
    pass


class PublicSubCategory(PublicCategory):
    pass


class InternalCategory(NewAbstractCategory):
    pass


class InternalSubCategory(InternalCategory):
    pass
