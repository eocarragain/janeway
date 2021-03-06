__copyright__ = "Copyright 2017 Birkbeck, University of London"
__author__ = "Martin Paul Eve & Andy Byers"
__license__ = "AGPL v3"
__maintainer__ = "Birkbeck Centre for Technology and Publishing"


from django.db import models
from submission import models as submission_models
from identifiers import logic

from utils import setting_handler
import sys


identifier_choices = (
    ('doi', 'DOI'),
    ('uri', 'URI'),
    ('pubid', 'Publisher ID'),
)


class Identifier(models.Model):
    id_type = models.CharField(max_length=300, choices=identifier_choices)
    identifier = models.CharField(max_length=300)
    enabled = models.BooleanField(default=True)
    article = models.ForeignKey(submission_models.Article, on_delete=models.CASCADE)

    def __str__(self):
        if self.is_doi:
            return u'{0}{1}{2}'.format(setting_handler.get_setting('Identifiers',
                                                                   'doi_display_prefix',
                                                                   self.article.journal).processed_value,
                                       self.identifier,
                                       setting_handler.get_setting('Identifiers',
                                                                   'doi_display_suffix',
                                                                   self.article.journal).processed_value
                                       )

        return u'[{0}]: {1}'.format(self.id_type.upper(), self.identifier)

    def register(self):
        if self.is_doi:
            logic.register_crossref_doi(self)
        else:
            print("Not a DOI", file=sys.stderr)

    def get_doi_url(self):
        if self.is_doi:
            return 'https://doi.org/{0}'.format(self.identifier)
        else:
            return 'This identifier is not a DOI.'

    @property
    def is_doi(self):
        if self.id_type == 'doi':
            return True

        return False


class BrokenDOI(models.Model):
    article = models.ForeignKey('submission.Article')
    identifier = models.ForeignKey(Identifier)
    checked = models.DateTimeField()
    resolves_to = models.URLField()
    expected_to_resolve_to = models.URLField()
