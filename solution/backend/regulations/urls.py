from django.contrib.auth import views as auth_views
from django.urls import include, path, register_converter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from regulations import converters
from regulations.views.about import AboutView
from regulations.views.cache import CacheView
from regulations.views.goto import GoToRedirectView
from regulations.views.homepage import HomepageView
from regulations.views.policy_repository import PolicyRepositoryView
from regulations.views.reader import (
    PartReaderView,
    SectionReaderView,
    SubpartReaderView,
)
from regulations.views.redirect import RegulationRedirectView
from regulations.views.regulation_landing import RegulationLandingView
from regulations.views.resources import ResourcesView
from regulations.views.search import SearchView
from regulations.views.statute import StatuteView
from regulations.views.statutes import ActListViewSet, StatuteLinkConverterViewSet
from regulations.views.supplemental_content import SupplementalContentView

register_converter(converters.NumericConverter, 'numeric')
register_converter(converters.SubpartConverter, 'subpart')
register_converter(converters.VersionConverter, 'version')

urlpatterns = [
    path('', HomepageView.as_view(), name='homepage'),
    path('about/', AboutView.as_view(), name='about'),
    path('<numeric:title>/<numeric:part>/', RegulationLandingView.as_view(), name="regulation_landing_view"),
    path('<numeric:title>/<numeric:part>/', RegulationLandingView.as_view(), name="reader_view"),
    path('<numeric:title>/<numeric:part>/<numeric:section>/', SectionReaderView.as_view(), name='reader_view'),
    path('<numeric:title>/<numeric:part>/<numeric:section>/<version:version>/', SectionReaderView.as_view(), name='reader_view'),
    path('<numeric:title>/<numeric:part>/Subpart-<subpart:subpart>/<version:version>/',
         SubpartReaderView.as_view(),
         name="reader_view"),
    path('<numeric:title>/<numeric:part>/Subpart-<subpart:subpart>/',
         SubpartReaderView.as_view(),
         name="reader_view"),
    path('<numeric:title>/<numeric:part>/<version:version>/', PartReaderView.as_view(), name='reader_view'),
    path('goto/', GoToRedirectView.as_view(), name='goto'),
    path('search/', SearchView.as_view(), name='search'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('supplemental_content/<id>/', SupplementalContentView.as_view(), name='supplemental_content'),
    path('cache/', CacheView.as_view(), name='cache'),
    path('resources/', ResourcesView.as_view(), name='resources'),
    path('statutes/', StatuteView.as_view(), name='statutes'),
    path('reg_redirect/', RegulationRedirectView.as_view(), name="reg_redirect"),
    path('policy-repository/', PolicyRepositoryView.as_view(), name='policy-repository'),
    path("v3/", include([
        path("statutes", StatuteLinkConverterViewSet.as_view({
            "get": "list",
        })),
        path("acts", ActListViewSet.as_view({
            "get": "list",
        })),
    ])),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
