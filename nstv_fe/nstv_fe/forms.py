from django import forms

title_choices = (
    (1, 'Beat Bobby Flay'), (2, 'Chopped'), (3, 'House Hunters'),
    (4, 'House Hunters International'), (5, 'Escape to the Chateau'),
    (6, 'Chopped Junior'), (7, 'Big Time Bake')
)


class DownloadForm(forms.Form):
    show_title = forms.ChoiceField(
        label='Show Title',
        choices=title_choices
    )
    season_number = forms.IntegerField(label='season_number')
    episode_number = forms.IntegerField(label='episode_number')


class AddShowForm(forms.Form):
    title = forms.CharField(label='Show Title')

