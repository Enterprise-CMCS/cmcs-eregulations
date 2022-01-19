from django.urls import path, register_converter

from regulations.views.reader import SubpartReaderView, SectionReaderView, PartReaderView
from regulations.views.goto import GoToRedirectView
from regulations.views.search import SearchView
from regulations.views.regulation_landing import RegulationLandingView
from regulations.views.homepage import HomepageView
from regulations.views.about import AboutView
from regulations import converters

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
    path('<numeric:title>/<numeric:part>/<version:version>/', PartReaderView.as_view(), name='reader_view'),
    path('goto/', GoToRedirectView.as_view(), name='goto'),
    path('search/', SearchView.as_view(), name='search'),
]
