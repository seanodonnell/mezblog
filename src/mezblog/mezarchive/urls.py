from django.conf.urls import url, patterns

urlpatterns = patterns("",
url("^archive/$" ,
        "mezarchive.views.blog_post_archive", name="blog_archive"
    ),
)
