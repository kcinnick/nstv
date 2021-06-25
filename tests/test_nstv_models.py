import os

import pytest

from nstv import models
from nstv.nstv import get_db_session

SKIP_REASON = "not on local, can't hit database."


@pytest.mark.skipif(type(os.getenv("POSTGRES_PASSWORD")) != str, reason=SKIP_REASON)
def test_episode_model():
    db_session = get_db_session()
    episode = db_session.query(models.Episode).where(models.Episode.id == 1).first()
    assert str(episode) == 'Pasta, Potatoes and Pescatarian'
