from django.conf import settings
from django.forms.models import modelform_factory
from django.forms import ValidationError

from drum.links.models import Link


BaseLinkForm = modelform_factory(Link, fields=["title", "description","link"])
#BaseLinkForm = modelform_factory(Link, fields=["title", "link", "description"])

class LinkForm(BaseLinkForm):

    def clean(self):
        link = self.cleaned_data.get("link", None)
        description = self.cleaned_data.get("description", None)
#        keywords_string = self.cleaned_data.get("keywords", None)
        if not description:
            raise ValidationError("Description is required")
#        if not link and not description:
#            raise ValidationError("Either a link or description is required")
        return self.cleaned_data
