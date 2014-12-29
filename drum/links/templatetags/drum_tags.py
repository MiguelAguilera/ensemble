from __future__ import unicode_literals

from collections import defaultdict
from django import template
from django.template.defaultfilters import timesince

from drum.links.utils import order_by_score
from drum.links.views import CommentList


register = template.Library()


@register.simple_tag(takes_context=True)
def order_comments_by_score_for(context, link):
    """
    Preloads threaded comments in the same way Mezzanine initially does,
    but here we order them by score.
    """
    comments = defaultdict(list)
    qs = link.comments.visible().select_related("user", "user__profile")
    for comment in order_by_score(qs, "submit_date",'top'):
        comments[comment.replied_to_id].append(comment)
    context["all_comments"] = comments
    return ""


@register.filter
def short_timesince(date):
    return timesince(date).split(",")[0]
