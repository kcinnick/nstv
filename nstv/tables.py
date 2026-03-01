import os

import django
import django_tables2 as tables
from django.utils.html import format_html, mark_safe

django.setup()

from .models import Show, Episode, Movie


class ShowIdColumn(tables.Column):
    def render(self, value):
        return format_html('<a href="/shows/{}" show>{}</a>', value, value)


class TvTitleColumn(tables.Column):
    def render(self, value):
        id_for_title = Show.objects.get(title=value).id
        return format_html('<a href="/shows/{}" show>{}</a>', id_for_title, value)


class TvGidColumn(tables.Column):
    def render(self, value):
        return format_html('<a href="https://nzbgeek.info/geekseek.php?tvid={}" show>{}</a>', value, value)


class EpisodeIdColumn(tables.Column):
    def render(self, value):
        return format_html('{}', value)


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
        return format_html('<a href="/movies/{}">{}</a>', value, value)


class GenreColumn(tables.Column):
    def render(self, value):
        if not value:
            return ''
        # value is an array of genres
        genre_links = []
        for genre in value:
            genre_links.append(format_html(
                '<a href="/movies/genre/{}" style="color: #667eea; text-decoration: none; margin-right: 8px;">{}</a>',
                genre, genre
            ))
        return mark_safe(' '.join(genre_links))


class DirectorColumn(tables.Column):
    def render(self, value):
        if not value:
            return ''
        return format_html(
            '<a href="/movies/director/{}" style="color: #667eea; font-weight: 600; text-decoration: none;">{}</a>',
            value, value
        )


class MovieTitleColumn(tables.Column):
    def render(self, value, record):
        return format_html(
            '<a href="/movies/{}" style="color: #667eea; font-weight: 600; text-decoration: none;">{}</a>',
            record.id, value
        )


class ShowTable(tables.Table):
    gid = TvGidColumn()
    id = ShowIdColumn()
    title = TvTitleColumn()
    tvdb_id = tables.Column(attrs={"th": {"id": "tvdb_id"}})
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
    name = MovieTitleColumn(attrs={"th": {"id": "name"}}, verbose_name="Title")
    release_date = tables.Column(attrs={"th": {"id": "release_date"}})
    genre = GenreColumn(attrs={"th": {"id": "genre"}})
    director = DirectorColumn(attrs={"th": {"id": "director"}})
    delete = DeleteMovieColumn()
    download = DownloadMovieColumn()

    class Meta:
        model = Movie
        template_name = "django_tables2/bootstrap.html"
        row_attrs = {
            "data-id": lambda record: record.pk,
        }
