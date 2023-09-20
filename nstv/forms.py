from django import forms
from .models import Show


class DownloadForm(forms.Form):
    title_choices = (
        (show.id, show.title) for show in Show.objects.all().order_by("id")
    )
    show_title = forms.ChoiceField(
        label='Show Title',
        choices=title_choices
    )
    season_number = forms.IntegerField(label='season_number')
    episode_number = forms.IntegerField(label='episode_number')


class AddShowForm(forms.Form):
    title = forms.CharField(label='Show Title')
