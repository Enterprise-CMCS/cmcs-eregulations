from django.contrib.sitemaps import Sitemap
from datetime import datetime

class PartSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return [{'title':42, 'part': 400}, {'title':42, 'part': 410}]

    def lastmod(self, obj):
        return datetime.now()

    def location(self, item):
        return f"/{item.title}/{item.part}"
