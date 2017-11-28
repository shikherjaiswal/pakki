"""Pakki_Seat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from . import views
from .views import StationAutocomplete

app_name = 'trains'

urlpatterns = [
    url(r'^search/sd/$', views.search_sd, name='search_sd'),
    url(r'^search/train/$', views.search_train, name='search_train'),
    url(r'^live/train/$', views.live_train, name='live_train'),
    url(r'^pnrStatus/train/$', views.pnrStatus, name='pnrStatus'),
    url(r'^fareEnquiry/train/$', views.fareEnquiry, name='fareEnquiry'),
    url(r'^$', views.index, name = 'index'),
    #url(r'^register/$', views.UserFormView.as_view(), name='user-register'),
    url(r'^login/$', views.login_view , name = 'user-login'),
    url(r'^logout/$', views.logout_view, name='user-logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^station-autocomplete/$', views.StationAutocomplete.as_view(), name='station-autocomplete'),
]
