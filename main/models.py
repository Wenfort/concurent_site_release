from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class HandledXml(models.Model):
    request_id = models.IntegerField(default=0)
    xml = models.TextField()
    status = models.CharField(max_length=10)
    geo = models.IntegerField(default=225)
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


class DomainGroup(models.Model):
    group_name = models.CharField(max_length=20)


class Payload(models.Model):
    key = models.CharField(max_length=100, primary_key=True)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.key} ({self.balance})'


class Region(models.Model):
    region_id = models.IntegerField(primary_key=True, default=0)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


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
    region = models.ForeignKey(Region, default=255, on_delete=models.DO_NOTHING)
    request_views = models.IntegerField(default=0)
    average_age = models.IntegerField(default=0)
    average_volume = models.IntegerField(default=0)
    average_total_backlinks = models.IntegerField(default=0)
    average_unique_backlinks = models.IntegerField(default=0)
    vital_sites = models.CharField(max_length=100, default = '')
    vital_sites_count = models.SmallIntegerField(default= 0)
    is_direct_final = models.SmallIntegerField(default=0)


    def __str__(self):
        return self.request_text



class UserData(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)
    orders_amount = models.IntegerField(default=0)
    ordered_keywords = models.IntegerField(default=0)
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, default=255)


class OrderStatus(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.SmallIntegerField(default=0)
    progress = models.SmallIntegerField(default=0)
    ordered_keywords_amount = models.SmallIntegerField(default=0)
    user_order_id = models.IntegerField(default=1)


class Order(models.Model):
    order = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)


class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=15, default='pending')
    opened = models.DateTimeField(default=timezone.now)
    closed = models.DateTimeField(blank=True, null=True)
    user_ticket_id = models.IntegerField(default=1)

    def __str__(self):
        return self.author


class TicketPost(models.Model):
    ticket_post_id = models.AutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.DO_NOTHING)
    ticket_post_author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    ticket_post_text = models.TextField(default='')
    ticket_post_order = models.SmallIntegerField(default=0)


class RequestQueue(models.Model):
    request_id = models.IntegerField(default=0)
    geo = models.IntegerField(default=255)
    is_recheck = models.BooleanField(default=False)


class SuperSites(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    unique_backlinks = models.IntegerField(default=0)
    total_backlinks = models.IntegerField(default=0)