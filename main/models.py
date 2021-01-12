from django.db import models


class Domain(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    age = models.IntegerField(default=0)
    unique_backlinks = models.IntegerField(default=0)
    total_backlinks = models.IntegerField(default=0)
    status = models.CharField(max_length=10, default='pending')

    def __str__(self):
        return self.name


class Payload(models.Model):
    key = models.CharField(max_length=100, primary_key=True)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.key} ({self.balance})'


class Request(models.Model):
    request = models.CharField(max_length=100)
    site_age_concurency = models.IntegerField(default=0)
    site_stem_concurency = models.IntegerField(default=0)
    site_volume_concurency = models.IntegerField(default=0)
    site_backlinks_concurency = models.IntegerField(default=0)
    site_total_concurency = models.FloatField(default=0)
    direct_upscale = models.FloatField(default=0)
    status = models.CharField(max_length=100, default='progress')

    def __str__(self):
        return self.request


class UserStatement(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    balance = models.IntegerField(default=0)
    ordered_requests = models.TextField()

    def __str__(self):
        return self.name


class RequestQueue(models.Model):
    request = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.request


class HandledXml(models.Model):
    request = models.CharField(max_length=100, primary_key=True)
    xml = models.TextField()
    status = models.CharField(max_length=10)

    def __str__(self):
        return self.request
