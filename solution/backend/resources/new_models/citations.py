from django.db import models

from common.mixins import DisplayNameFieldMixin


class AbstractCitation(models.Model, DisplayNameFieldMixin):
    pass


class NewSubpart(AbstractCitation):
    pass


class NewSection(AbstractCitation):
    pass
