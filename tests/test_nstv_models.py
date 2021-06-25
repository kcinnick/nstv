from nstv import models
from nstv.nstv import get_db_session


def test_episode_model():
    db_session = get_db_session()
    episode = db_session.query(models.Episode).where(models.Episode.id == 1).first()
    assert str(episode) == 'Pasta, Potatoes and Pescatarian'
