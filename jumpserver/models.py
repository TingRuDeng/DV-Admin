# coding: utf-8

from django.db import models
from juser.models import User, role
# import random
# import hashlib

#
# def menu_md5():
#     list = str(random.uniform(1,10))
#     menu = hashlib.md5()
#     menu.update(list)
#     menu_md5_value = menu.hexdigest()[:8]
#     return menu_md5_value


class Setting(models.Model):
    name = models.CharField(max_length=100)
    field1 = models.CharField(max_length=100, null=True, blank=True)
    field2 = models.CharField(max_length=100, null=True, blank=True)
    field3 = models.CharField(max_length=256, null=True, blank=True)
    field4 = models.CharField(max_length=100, null=True, blank=True)
    field5 = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'setting'

    def __unicode__(self):
        return self.name

