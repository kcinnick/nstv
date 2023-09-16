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


class DownloadColumn(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        download_html_str = '''
        <form action="/shows/{{ record.show_id }}/episode/{{ record.id }}/download" method="post">
            {% csrf_token %}
            <input type="submit" value="Download" />
        </form>'''
        super().__init__(template_code=download_html_str, *args, **kwargs)


class DeleteColumn(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        delete_html_str = '''
        <form action="/delete/{{ record.id }}" method="post">
            {% csrf_token %}
            <input type="submit" value="Delete" />
        </form>'''
        super().__init__(template_code=delete_html_str, *args, **kwargs)


class ShowTable(tables.Table):
    gid = tables.Column(attrs={"th": {"id": "gid"}})
    id = ShowIdColumn()
    title = tables.Column(attrs={"th": {"id": "title"}})
    start_date = tables.Column(attrs={"th": {"id": "start_date"}})
    end_date = tables.Column(attrs={"th": {"id": "end_date"}})
    delete = DeleteColumn()

    class Meta:
        model = Show
        template_name = "django_tables2/bootstrap.html"
        row_attrs = {
            "data-id": lambda record: record.pk,
        }


class EpisodeTable(tables.Table):
    id = EpisodeIdColumn()
    title = tables.Column(attrs={"th": {"id": "title"}})
    season_number = tables.Column(attrs={"th": {"id": "season_number"}})
    download = DownloadColumn()

    class Meta:
        model = Episode
        template_name = "django_tables2/bootstrap.html"
        row_attrs = {
            "data-id": lambda record: record.pk,
        }
