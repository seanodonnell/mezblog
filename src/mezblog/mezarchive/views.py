from mezzanine.conf import settings
from mezzanine.blog.models import BlogPost
from mezzanine.utils.views import render


def blog_post_archive(request, template="blog/blog_post_list.html"):
    """
    Display all blog posts
    """
    settings.use_editable()

    blog_posts = BlogPost.objects.published(for_user=request.user)

    prefetch = ("categories", "keywords__keyword")
    blog_posts = blog_posts.select_related("user").prefetch_related(*prefetch)

    class ObjectList(object):
        def __init__(self, object_list):
            self.object_list = object_list

    context = {"blog_posts": ObjectList(blog_posts)}
    return TemplateResponse(request, "blog/blog_post_list.html", context)
