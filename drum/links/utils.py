from __future__ import division
from __future__ import unicode_literals

from django.conf import settings
from django.utils.timezone import now
from math import log10
import datetime

def order_by_score(queryset, score_fields, date_field, reverse=True, T=1):
    """
    Take some queryset (links or comments) and order them by score,
    which is basically "rating_sum / age_in_seconds ^ scale", where
    scale is a constant that can be used to control how quickly scores
    reduce over time. To perform this in the database, it needs to
    support a POW function, which Postgres and MySQL do. For databases
    that don't such as SQLite, we perform the scoring/sorting in
    memory, which will suffice for development.
    """

    scale = getattr(settings, "SCORE_SCALE_FACTOR", 2)
    timeweight = 45000.0 * T
	
    # Timestamp SQL function snippets mapped to DB backends.
    # Defining these assumes the SQL functions POW() and NOW()
    # are available for the DB backend.
    timestamp_sqls = {
        "mysql": "UNIX_TIMESTAMP(%s)",
        "postgresql_psycopg2": "EXTRACT(EPOCH FROM %s)" ,
    }
    db_engine = settings.DATABASES[queryset.db]["ENGINE"].rsplit(".", 1)[1]
    timestamp_sql = timestamp_sqls.get(db_engine)
    print 'database', timestamp_sql

    if timestamp_sql:
        score_sql = "(%s) / POW(%s - %s, %s)" % (
            " + ".join(score_fields),
            timestamp_sql % "NOW()",
            timestamp_sql % date_field,
            scale,
        )
        order_by = "-score" if reverse else "score"
        return queryset.extra(select={"score": score_sql}).order_by(order_by)
    else:
        for obj in queryset:
			seconds = (getattr(obj, date_field).replace(tzinfo=None) - datetime.datetime.fromtimestamp(1134028003)).total_seconds() 
			s = sum([getattr(obj, f) for f in score_fields])
			order = log10(max(abs(s)+1, 1))
			if s > 0:
				sign = 1
			elif s < 0:
				sign = -1
			else:
				sign = 0
			score = round(sign * order + seconds / timeweight, 7)				
			setattr(obj, "score", score)
        return sorted(queryset, key=lambda obj: obj.score, reverse=reverse)
        
def order_by_consesus(queryset, score_fields, date_field, reverse=True, T=1):
    """
    Take some queryset (links or comments) and order them by score,
    which is basically "rating_sum / age_in_seconds ^ scale", where
    scale is a constant that can be used to control how quickly scores
    reduce over time. To perform this in the database, it needs to
    support a POW function, which Postgres and MySQL do. For databases
    that don't such as SQLite, we perform the scoring/sorting in
    memory, which will suffice for development.
    """

    scale = getattr(settings, "SCORE_SCALE_FACTOR", 2)
    timeweight = 45000.0 * T
	
    # Timestamp SQL function snippets mapped to DB backends.
    # Defining these assumes the SQL functions POW() and NOW()
    # are available for the DB backend.
    timestamp_sqls = {
        "mysql": "UNIX_TIMESTAMP(%s)",
        "postgresql_psycopg2": "EXTRACT(EPOCH FROM %s)" ,
    }
    db_engine = settings.DATABASES[queryset.db]["ENGINE"].rsplit(".", 1)[1]
    timestamp_sql = timestamp_sqls.get(db_engine)
    print 'database', timestamp_sql

    if timestamp_sql:
        score_sql = "(%s) / POW(%s - %s, %s)" % (
            " + ".join(score_fields),
            timestamp_sql % "NOW()",
            timestamp_sql % date_field,
            scale,
        )
        order_by = "-score" if reverse else "score"
        return queryset.extra(select={"score": score_sql}).order_by(order_by)
    else:
        for obj in queryset:
			seconds = (getattr(obj, date_field).replace(tzinfo=None) - datetime.datetime.fromtimestamp(1134028003)).total_seconds() 
			s = sum([getattr(obj, f) for f in score_fields])
			order = log10(max(abs(s)+1, 1))
			if s > 0:
				sign = 1
			elif s < 0:
				sign = -1
			else:
				sign = 0
			score = round(sign * order + seconds / timeweight, 7)				
			setattr(obj, "score", score)
        return sorted(queryset, key=lambda obj: obj.score, reverse=reverse)

