from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


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


class RequestQueue(models.Model):
    request_text = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.request_text


class Request(models.Model):
    request_id = models.AutoField(primary_key=True)
    request_text = models.CharField(max_length=100)
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
        return self.request_text


class HandledXml(models.Model):
    request = models.CharField(max_length=100, primary_key=True)
    xml = models.TextField()
    status = models.CharField(max_length=10)

    def __str__(self):
        return self.request


class UserData(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)
    orders_amount = models.IntegerField(default=0)
    ordered_keywords = models.IntegerField(default=0)


class OrderStatus(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.SmallIntegerField(default=0)
    progress = models.SmallIntegerField(default=0)
    ordered_keywords_amount = models.SmallIntegerField(default=0)


class Order(models.Model):
    order = models.ForeignKey(OrderStatus, on_delete=models.DO_NOTHING)
    request = models.ForeignKey(Request, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)


class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=15, default='pending')
    opened = models.DateTimeField(default=timezone.now)
    closed = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.author


class TicketPost(models.Model):
    ticket_post_id = models.AutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.DO_NOTHING)
    ticket_post_author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    ticket_post_text = models.TextField(default='')
    ticket_post_order = models.SmallIntegerField(default=0)