"""
Root URLs for CCX Connector
"""
from django.conf.urls import include, url
from django.contrib import admin

from rest_framework_nested import routers

from courses.views import CourseViewSet, ModuleViewSet

router = routers.DefaultRouter()
router.register('coursexs', CourseViewSet)

modules_router = routers.NestedSimpleRouter(router, 'coursexs', lookup='uuid')
modules_router.register('modules', ModuleViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/', include(modules_router.urls)),
]
