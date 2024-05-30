from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class DepartmentGroup(models.Model):
    name = models.CharField(max_length=512, null=False, blank=False, unique=True)
    abbreviation = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.name


class Division(models.Model):
    department_group = models.ForeignKey(DepartmentGroup,
                                         blank=True,
                                         null=True,
                                         related_name="divisions",
                                         on_delete=models.SET_NULL)
    name = models.CharField(max_length=512,
                            null=False,
                            blank=False,
                            unique=True)
    abbreviation = models.CharField(max_length=64,
                                    null=True,
                                    blank=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True, default='')
    department_group = models.ForeignKey(DepartmentGroup,
                                         on_delete=models.SET_NULL,
                                         null=True,
                                         blank=True)
    division = models.ForeignKey(Division,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


def set_department_group_and_division(profile):
    department_parts = profile.department.split('/')
    if len(department_parts) >= 6:
        group_name = department_parts[5]
        department_group, _ = DepartmentGroup.objects.get_or_create(name=group_name)
        profile.department_group = department_group
    if len(department_parts) >= 7:
        division_name = department_parts[6]
        division, _ = Division.objects.get_or_create(name=division_name, department_group=profile.department_group)
        profile.division = division
    profile.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        set_department_group_and_division(profile)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        set_department_group_and_division(instance.profile)
        instance.profile.save()
