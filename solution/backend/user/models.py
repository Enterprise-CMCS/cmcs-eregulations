from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class DepartmentGroup(models.Model):
    name = models.CharField(max_length=512, null=False, blank=False, unique=True)
    abbreviation = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.name


class DepartmentDivision(models.Model):
    department_group = models.ForeignKey(DepartmentGroup,
                                         blank=True,
                                         null=True,
                                         related_name="department_divisions",
                                         on_delete=models.SET_NULL)
    name = models.CharField(max_length=512, null=False, blank=False, unique=True)
    abbreviation = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True, default='')
    department_group = models.ForeignKey(DepartmentGroup, on_delete=models.SET_NULL, null=True, blank=True)
    department_division = models.ForeignKey(DepartmentDivision, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


def set_department_group_and_division(profile, save_profile=True):
    if not profile.department:
        return

    profile.department_group = None
    profile.department_division = None

    department_parts = profile.department.split('/')
    if len(department_parts) >= 6:
        group_name = department_parts[5]
        department_group, _ = DepartmentGroup.objects.get_or_create(name=group_name)
        profile.department_group = department_group
    if len(department_parts) >= 7:
        division_name = department_parts[6]
        department_division, _ = DepartmentDivision.objects.get_or_create(
            name=division_name,
            department_group=profile.department_group
        )
        profile.department_division = department_division

    if save_profile:
        profile.save()


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    profile = Profile.objects.create(user=instance) if created else instance.profile
    set_department_group_and_division(profile, save_profile=False)
    profile.save()
