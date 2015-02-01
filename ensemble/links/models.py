# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from future import standard_library
from future.builtins import int

from re import sub, split
from time import time
from operator import ior

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from mezzanine.core.models import Displayable, Ownable
from mezzanine.core.request import current_request
from mezzanine.generic.models import Rating, Keyword, AssignedKeyword
from mezzanine.generic.fields import RatingField, CommentsField
from mezzanine.utils.urls import slugify

USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

class Link(Displayable, Ownable):

    link = models.URLField(null=True,
        blank=(not getattr(settings, "LINK_REQUIRED", False)))
    rating = RatingField()
    comments = CommentsField()
    
    taglist=['Municipalismo','Educación','Cultura']
    tag_choices = [('None', '---')]
    for tag in taglist:
        tag_choices = tag_choices + [(tag,tag)]
    tags = models.CharField(max_length=50, choices=tag_choices, default='')
    def get_absolute_url(self):
        return reverse("link_detail", kwargs={"slug": self.slug})

    @property
    def domain(self):
        return urlparse(self.url).netloc

    @property
    def url(self):
#		Uncomment for direct to link when clicking in item
#        if self.link:
#        	return self.link
        return current_request().build_absolute_uri(self.get_absolute_url())

    def save(self, *args, **kwargs):
        
        keywords = []
        if not self.keywords_string and getattr(settings, "AUTO_TAG", False):
            variations = lambda word: [word,
                sub("^([^A-Za-z0-9])*|([^A-Za-z0-9]|s)*$", "", word),
                sub("^([^A-Za-z0-9])*|([^A-Za-z0-9])*$", "", word)]
            keywords = sum(map(variations, split("\s|/", self.tags)), [])
        super(Link, self).save(*args, **kwargs)
        if keywords:
            lookup = reduce(ior, [Q(title__iexact=k) for k in keywords])
            for k in keywords:
            	if k!='None':
            	    Keyword.objects.get_or_create(title=k)
            for keyword in Keyword.objects.filter(lookup):
                self.keywords.add(AssignedKeyword(keyword=keyword))
        

class Profile(models.Model):

    user = models.OneToOneField(USER_MODEL)
#    website = models.URLField(blank=True)
#    bio = models.TextField(blank=True)
    website = models.URLField(blank=True, editable=False)
    bio = models.TextField(blank=True, editable=False)
    karma = models.IntegerField(default=0, editable=False)

    def __unicode__(self):
        return "%s (%s)" % (self.user, self.karma)


@receiver(post_save, sender=Rating)
def karma(sender, **kwargs):
    """
    Each time a rating is saved, check its value and modify the
    profile karma for the related object's user accordingly.
    Since ratings are either +1/-1, if a rating is being edited,
    we can assume that the existing rating is in the other direction,
    so we multiply the karma modifier by 2.
    """
    rating = kwargs["instance"]
    value = int(rating.value)
    if not kwargs["created"]:
        value *= 2
    content_object = rating.content_object
    if rating.user != content_object.user:
        queryset = Profile.objects.filter(user=content_object.user)
        queryset.update(karma=models.F("karma") + value)
