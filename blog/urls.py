from django.urls import path
from .views import *
from django.contrib.sitemaps.views import sitemap
from .sitemaps import PostSitemap
from .feeds import LatestPostFeed

app_name = 'blog'

sitemaps = {'post': PostSitemap}

urlpatterns = [
    path('list/', PostList.as_view(), name='PostList'),
    path('detail/<slug:slug>/', PostDetail.as_view(), name='PostDetail'),
    path('share/<int:post_id>/', PostShare.as_view(), name='PostShare'),
    path('list/<slug:tag_slug>', PostTagsList.as_view(), name='PostTagsList'),
    path('search/', SearchPost.as_view(), name='PostSearch'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('feed/', LatestPostFeed(), name='PostsFeed'),
]
