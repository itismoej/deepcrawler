from django.urls import path

from crawler.views import site, crawl

urlpatterns = [
    path('sites/<int:site_id>/', site),
    path('crawls/<int:crawl_id>/', crawl),
]
