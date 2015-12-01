"""
Root URLs for CCX Connector
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

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
    url(r'^api/v1/user_exists/$', 'courses.views.user_existence', name='user-existence'),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]

urlpatterns += staticfiles_urlpatterns()
