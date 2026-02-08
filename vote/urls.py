from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from django.contrib.auth import views as auth_views

from .views import *


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home_view, name = 'home'),
    path('vote/<str:token>', home_view, name = 'home'),
    path('control', control_view, name = 'control'),
    path('logout', logout_view, name = 'logout'),
    path('login', login_view, name = 'login'),
    path('policy', policy_view, name = 'policy'),

    path('concerted', concerted_view, name = 'concerted'),
]


urlpatterns += [
    path('profile/', include(('profileuser.urls', 'profile'))),
    path('publicvotes/', include(('publicvotes.urls', 'publicvotes'))),
]



urlpatterns += [
    path('ajax/allow-cookies/', allow_cookies, name = 'ajax_allow_cookies'),
]