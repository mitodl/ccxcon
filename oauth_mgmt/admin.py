"""
Admin
"""
from django.contrib import admin
from .models import BackingInstance


admin.site.register(BackingInstance)
