from __future__ import unicode_literals
from django.db import models

# Create your models here.
class role(models.Model):
    user_name = models.CharField(max_length=50,null='False', blank='False')
    user_role = models.CharField(max_length=50,null='False', blank='False')

    def __str__(self):
        return '{0} {1}'.format(self.user_name, self.user_role)

class Login(models.Model):
    user = models.CharField(max_length=100,null='False',blank='False')
    login_status = models.CharField(max_length=100,null='False',blank='False')
    login_time = models.DateTimeField(null='True', blank='True')
    benchmark_hours = models.IntegerField(null='False', blank='False')

    def __str__(self):
        return '{0} {1} {2}'.format(self.user, self.login_status, self.benchmark_hours)