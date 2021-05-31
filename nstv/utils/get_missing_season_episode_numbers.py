from nstv_fe.nstv_fe.models import Episode
from nstv.nstv import get_db_session
import imdb
ia = imdb.IMDb()


def search_episode(episode_title):
    episode = Episode.objects.filter(title=episode_title).first()
    results = ia.search_episode(episode.title)
    season_number, episode_number = results[0].data['season'], results[0].data['episode']
    print('season: {}'.format(str(season_number) + ' ' + str(episode_number)))
    episode.season_number = season_number
    episode.number = episode_number
    episode.save()
