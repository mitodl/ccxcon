"""
Admin for courses and overrides for django's User model
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OldUserAdmin
from django.contrib.auth.models import User

from courses.forms import RequiredInlineFormSet
from courses.models import UserInfo


class UserInfoInline(admin.StackedInline):
    """
    Inline for showing user's info.
    """
    model = UserInfo
    can_delete = False
    max_num = 1
    min_num = 1
    formset = RequiredInlineFormSet


class UserAdmin(OldUserAdmin):
    """
    Custom UserAdmin which shows info pane.
    """
    inlines = (UserInfoInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
