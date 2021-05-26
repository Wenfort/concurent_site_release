from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Region(models.Model):
    id = models.IntegerField(primary_key=True, default=0)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.SmallIntegerField(default=0)
    progress = models.SmallIntegerField(default=0)
    ordered_keywords_amount = models.SmallIntegerField(default=0)
    user_order_id = models.IntegerField(default=1)

class Request(models.Model):
    text = models.CharField(max_length=150)
    age_concurency = models.IntegerField(default=0)
    stem_concurency = models.IntegerField(default=0)
    volume_concurency = models.IntegerField(default=0)
    backlinks_concurency = models.IntegerField(default=0)
    total_concurency = models.FloatField(default=0)
    direct_upscale = models.FloatField(default=0)
    seo_concurency = models.IntegerField(default=0)
    direct_concurency = models.IntegerField(default=0)
    status = models.CharField(max_length=100, default='progress')
    region = models.ForeignKey(Region, default=255, on_delete=models.DO_NOTHING)
    views = models.IntegerField(default=0)
    average_age = models.IntegerField(default=0)
    average_volume = models.IntegerField(default=0)
    average_total_backlinks = models.IntegerField(default=0)
    average_unique_backlinks = models.IntegerField(default=0)
    vital_sites = models.CharField(max_length=150, default='')
    vital_sites_count = models.SmallIntegerField(default=0)
    is_direct_final = models.SmallIntegerField(default=0)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class HandledXml(models.Model):
    request = models.OneToOneField(Request, on_delete=models.CASCADE)
    xml = models.TextField()
    status = models.CharField(max_length=10)
    region = models.ForeignKey(Region, default=255, on_delete=models.DO_NOTHING)
    refresh_timer = models.SmallIntegerField(default=10)
    reruns_count = models.SmallIntegerField(default=0)
    top_ads_count = models.SmallIntegerField(default=0)
    bottom_ads_count = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.request


class Domain(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    age = models.IntegerField(default=0)
    unique_backlinks = models.IntegerField(default=0)
    total_backlinks = models.IntegerField(default=0)
    status = models.CharField(max_length=10, default='pending')
    domain_group = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Payload(models.Model):
    key = models.CharField(max_length=100, primary_key=True)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.key} ({self.balance})'


class UserData(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)
    orders_amount = models.IntegerField(default=0)
    ordered_keywords = models.IntegerField(default=0)
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, default=255)

class RequestQueue(models.Model):
    request = models.OneToOneField(Request, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, default=255)
    is_recheck = models.BooleanField(default=False)


class TicketPost(models.Model):
    author = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    text = models.TextField()
    order = models.SmallIntegerField(default=0)


class Ticket(models.Model):
    author = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=15, default='pending')
    opened = models.DateTimeField(default=timezone.now)
    closed = models.DateTimeField(blank=True, null=True)
    user_ticket_id = models.IntegerField(default=1)
    posts = models.ForeignKey(TicketPost, on_delete=models.CASCADE)

    def __str__(self):
        return self.author
