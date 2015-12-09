"""
Webhook Admin
"""
from django.contrib import admin
from webhooks.models import Webhook

admin.site.register(Webhook)
