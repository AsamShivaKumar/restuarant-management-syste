from django.db import models

class TimeZone(models.Model):
    store_id = models.IntegerField()
    time_zone_str = models.CharField(max_length=50)

class WorkingHour(models.Model):
    store_id = models.IntegerField()
    day = models.IntegerField()
    start = models.CharField(max_length=8)
    end = models.CharField(max_length=8)

class Observation(models.Model):
    store_id = models.IntegerField()
    date = models.CharField(max_length=30)
    status = models.CharField(max_length=8)

class Report(models.Model):
    url = models.CharField(max_length=100) # file location
    status = models.CharField(max_length=8)