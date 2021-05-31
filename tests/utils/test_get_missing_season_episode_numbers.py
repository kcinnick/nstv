import os

from nstv.nstv import get_db_session
from nstv_fe.nstv_fe.models import Episode
from nstv.utils import get_missing_season_episode_numbers
from django.conf import settings

try:
    settings.configure(DEBUG=True)
except RuntimeError:
    pass


def test_search_episode():
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": os.getenv('POSTGRES_PASSWORD'),
            "HOST": "127.0.0.1",
            "PORT": "5432",
        }
    }

    test_episode = Episode.objects.filter(title='Taco Time!').first()
    test_episode.season_number = 0
    test_episode.number = 0
    test_episode.save()
    get_missing_season_episode_numbers.search_episode('Taco Time!')
    test_episode = Episode.objects.filter(title='Taco Time!').first()
    assert test_episode.season_number == 31
    assert test_episode.number == 18
