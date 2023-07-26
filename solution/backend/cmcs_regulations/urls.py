"""cmcs_regulations URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic.base import RedirectView, TemplateView
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth import views as auth_views
from regulations.sitemap import PartSitemap, SupplementalContentSitemap
from regulations.rss_feeds import ResourceFeed

sitemaps = {
    "Parts": PartSitemap,
    "SupplementalContent": SupplementalContentSitemap,
}

urlpatterns = [
    path('', include('regcore.urls')),
    path('', include('regulations.urls')),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'images/favicon/favicon.ico')),
    path('admin/login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('admin/', admin.site.urls, name="admin"),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('__debug__/', include('debug_toolbar.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('latest/feed/', ResourceFeed()),
]
admin.site.site_header = "Eregs"
admin.site.site_title = 'Eregs Admin Panel'
admin.site.index_title = 'Medicaid & Chip Eregulations Admin Panel'
