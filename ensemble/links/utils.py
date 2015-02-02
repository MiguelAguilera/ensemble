from __future__ import division
from __future__ import unicode_literals

from django.conf import settings
from django.utils.timezone import now
from math import log,log10
import datetime

def order_by_score(queryset, date_field, order, reverse=True, T=7):
    """
    Take some queryset (links or comments) and order them by the
    selected algorithm
    """
    timeweight = 45000.0 * 2 * T #Reddit -> T=0.5 - ~12h
    
    for obj in queryset:
        votes = getattr(obj, "rating_count")
        seconds = (getattr(obj, date_field).replace(tzinfo=None) - datetime.datetime.fromtimestamp(1134028003)).total_seconds() 
        s = getattr(obj, "rating_sum")
        score=s
        if order=='hot':
            sc = log10(max(abs(s)+1, 1))
            if s > 0:
                sign = 1
            elif s < 0:
                sign = -1
            else:
                sign = 0
            score = round(sign * sc + seconds / timeweight, 7)            
                
        if order=='consensus':
            p=(votes+s)*0.5
            n=(votes-s)*0.5
            if abs(votes)>0:
                score = log(1+p+n,2) * ((p-n)/(p+n)) 
            else:
                score=0
                
        if order=='latest':
            score=seconds
        
        if order=='top':
            score=s
                
        setattr(obj, "score", score)
    return sorted(queryset, key=lambda obj: obj.score, reverse=reverse)
