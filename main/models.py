from django.db import models
from django.utils import timezone

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
    site_seo_concurency = models.IntegerField(default=0)
    site_direct_concurency = models.IntegerField(default=0)
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


class UserData(models.Model):
    balance = models.IntegerField(default=0)
    name = models.CharField(max_length=30)
    orders_amount = models.IntegerField(default=0)
    ordered_keywords = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    order_id = models.IntegerField(default=0)
    request_id = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)


class OrderStatus(models.Model):
    order_id = models.IntegerField(primary_key=True, default=0)
    user_id = models.IntegerField(default=0)
    status = models.SmallIntegerField(default=0)
    progress = models.SmallIntegerField(default=0)
    ordered_keywords_amount = models.SmallIntegerField(default=0)


class Ticket(models.Model):
    author = models.CharField(max_length=25)
    status = models.CharField(max_length=15, default='pending')
    opened = models.DateTimeField(default=timezone.now)
    closed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.author

class TicketPost(models.Model):
    ticked_id = models.IntegerField(default=0)
    ticket_post_author = models.CharField(max_length=25, default='')
    ticket_post_text = models.TextField(default='')
    ticket_post_order = models.SmallIntegerField(default=0)