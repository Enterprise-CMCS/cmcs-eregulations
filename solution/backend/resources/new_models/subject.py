from django.db import models

from common.mixins import DisplayNameFieldMixin


class NewSubject(models.Model, DisplayNameFieldMixin):
    pass
