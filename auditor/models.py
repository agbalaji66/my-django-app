from __future__ import unicode_literals
from django.db import models

# Create your models here.
class DataLog(models.Model):
    UUID= models.AutoField(primary_key=True)
    associate = models.CharField(max_length=100,null='False', blank='False')
    date = models.DateField(null='True', blank='True')
    performed_date = models.DateField(null='True', blank='True')
    month = models.CharField(max_length=15,null='False', blank='False')
    task =  models.CharField(max_length=100,null='False', blank='False')
    Sub_Task = models.CharField(max_length=500,null='False', blank='False')
    filename = models.CharField(max_length=100,null='False', blank='False')
    volume=models.CharField(max_length=100, null='False', blank='False')
    hours_spent= models.DecimalField(max_digits=10, decimal_places=2,null='True', blank='True')
    Productivity=models.IntegerField(null='False', blank='False')
    status = models.CharField(max_length=15,null='False', blank='False')
    accuracy =  models.CharField(max_length=100,null='False', blank='False')
    aoa_by = models.CharField(max_length=500,null='False', blank='False')
    auditor_comments = models.CharField(max_length=500,null='False', blank='False')
    aoa_comments = models.CharField(max_length=500,null='False', blank='False')

class task_information(models.Model):
    Task_ID=models.AutoField(primary_key=True)
    Task=models.CharField(max_length=100, null='False', blank='False')
    Sub_Task=models.CharField(max_length=100, null='False', blank='False')
    volume=models.IntegerField(null='False', blank='False')
    benchmark=models.DecimalField(max_digits=5, decimal_places=2,null='True', blank='True')
    
    
    
                
    