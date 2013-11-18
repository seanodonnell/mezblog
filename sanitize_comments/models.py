from django.db import models
from mezzanine.generic.models import ThreadedComment
from sanitize import sanitize

from django.contrib.comments.signals import comment_will_be_posted

def comment_sanitizer(sender, comment, request, **kwargs):
    comment.comment = sanitize(comment.comment)
    print "********************************"
    print "Sanitizing"
    print "********************************"
comment_will_be_posted.connect(comment_sanitizer, sender=ThreadedComment)
