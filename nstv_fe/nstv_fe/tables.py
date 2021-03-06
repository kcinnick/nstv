import django_tables2 as tables
from django.utils.html import format_html

from nstv_fe.models import Show


class ShowIdColumn(tables.Column):
    def render(self, value):
        return format_html('<a href="/shows/{}" show>{}</a>'.format(value, value))


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
