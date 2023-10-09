import os

import django
import django_tables2 as tables
from django.utils.html import format_html

django.setup()

from .models import Show, Episode, Movie


class ShowIdColumn(tables.Column):
    def render(self, value):
        return format_html('<a href="/shows/{}" show>{}</a>'.format(value, value))


class EpisodeIdColumn(tables.Column):
    def render(self, value):
        return format_html('{}'.format(value, value, value))


class DownloadColumn(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        download_html_str = '''
        <form action="/shows/{{ record.show_id }}/episode/{{ record.id }}/download" method="post">
            {% csrf_token %}
            <input type="submit" value="Download" />
        </form>'''
        super().__init__(template_code=download_html_str, *args, **kwargs)


class DeleteShowColumn(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        delete_show_html_str = '''
        <form action="/delete/{{ record.id }}" method="post">
            {% csrf_token %}
            <input type="submit" value="Delete" />
        </form>'''
        super().__init__(template_code=delete_show_html_str, *args, **kwargs)


class DeleteEpisodeColumn(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        delete_episode_html_str = '''
        <form action="/delete/{{ record.show_id }}/episode/{{ record.id }}" method="post">
            {% csrf_token %}
            <input type="submit" value="Delete" />
        </form>'''
        super().__init__(template_code=delete_episode_html_str, *args, **kwargs)


class MovieIdColumn(tables.Column):
    def render(self, value):
        return format_html('<a href="/movies/{}" movie>{}</a>'.format(value, value))


class ShowTable(tables.Table):
    gid = tables.Column(attrs={"th": {"id": "gid"}})
    id = ShowIdColumn()
    title = tables.Column(attrs={"th": {"id": "title"}})
    # start_date = tables.Column(attrs={"th": {"id": "start_date"}})
    # end_date = tables.Column(attrs={"th": {"id": "end_date"}})
    delete = DeleteShowColumn()

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
    delete = DeleteEpisodeColumn()

    class Meta:
        model = Episode
        order_by = ('season_number', 'episode_number')
        template_name = "django_tables2/bootstrap.html"
        row_attrs = {
            "data-id": lambda record: record.pk,
        }


class DeleteMovieColumn(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        delete_movie_html_str = '''
        <form action="/delete/movies/{{ record.id }}" method="post">
            {% csrf_token %}
            <input type="submit" value="Delete" />
        </form>'''
        super().__init__(template_code=delete_movie_html_str, *args, **kwargs)


class DownloadMovieColumn(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        download_html_str = '''
        <form action="/movies/{{ record.id }}/download" method="post">
            {% csrf_token %}
            <input type="submit" value="Download" />
        </form>'''
        super().__init__(template_code=download_html_str, *args, **kwargs)


class MovieTable(tables.Table):
    id = MovieIdColumn()
    title = tables.Column(attrs={"th": {"id": "title"}})
    release_date = tables.Column(attrs={"th": {"id": "release_date"}})
    genre = tables.Column(attrs={"th": {"id": "genre"}})
    director = tables.Column(attrs={"th": {"id": "director"}})
    delete = DeleteMovieColumn()
    download = DownloadMovieColumn()

    class Meta:
        model = Movie
        template_name = "django_tables2/bootstrap.html"
        row_attrs = {
            "data-id": lambda record: record.pk,
        }
