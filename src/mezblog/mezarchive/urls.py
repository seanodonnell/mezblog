from django.conf.urls import url, patterns
from mezarchive import views


urlpatterns = [
    url("^archive/$", views.blog_post_archive, name="blog_archive"),
]
