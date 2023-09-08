import os

import django
import django_tables2 as tables
from django.utils.html import format_html

django.setup()

from .models import Show, Episode


class ShowIdColumn(tables.Column):
    def render(self, value):
        return format_html('<a href="/shows/{}" show>{}</a>'.format(value, value))


class EpisodeIdColumn(tables.Column):
    def render(self, value):
        return format_html('<a href="/episodes/{}" episode>{}</a>'.format(value, value, value))


class ShowTable(tables.Table):
    gid = tables.Column(attrs={"th": {"id": "foo"}})
    id = ShowIdColumn()
    title = tables.Column(attrs={"th": {"id": "fooTexT"}})
    start_date = tables.Column(attrs={"th": {"id": "foo2"}})
    end_date = tables.Column(attrs={"th": {"id": "foo2"}})

    class Meta:
        model = Show
        template_name = "django_tables2/bootstrap.html"
        row_attrs = {
            "data-id": lambda record: record.pk,
        }


class EpisodeTable(tables.Table):
    id = EpisodeIdColumn()
    title = tables.Column(attrs={"th": {"id": "fooTexT"}})
    season_number = tables.Column(attrs={"th": {"id": "foo2"}})
    episode_number = tables.Column(attrs={"th": {"id": "foo2"}})

    class Meta:
        model = Episode
        template_name = "django_tables2/bootstrap.html"
        row_attrs = {
            "data-id": lambda record: record.pk,
        }
