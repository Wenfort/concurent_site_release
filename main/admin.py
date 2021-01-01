from django.contrib import admin

from .models import Domain, Payload, Request

admin.site.register(Domain)
admin.site.register(Payload)
admin.site.register(Request)
