from sqlalchemy import (Column, Date, ForeignKey, Integer, MetaData, String,
                        Table)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
meta = MetaData()

shows = Table(
    "show",
    meta,
    Column("gid", Integer),
    Column("id", Integer, primary_key=True),
    Column("title", String, unique=True),
    Column("start_date", Date),
    Column("end_date", Date),
    Column("slug", String, unique=True),
)

episodes = Table(
    "episode",
    meta,
    Column("id", Integer, primary_key=True, unique=True),
    Column("show", String),
    Column("start_date", Date),
    Column("end_date", Date),
    Column("slug", String, unique=True),
    Column("season_number", String, unique=True),
    Column("number", String, unique=True),
)


class Episode(Base):
    __tablename__ = "episode"

    id = Column(Integer, primary_key=True, unique=True)
    show_id = Column(Integer, ForeignKey("show.id"))
    air_date = Column(Date)
    title = Column(String)
    slug = Column(String)  #  episode's title with all punctuation & non-alphanumeric chars removed
    season_number = Column(Integer),
    number = Column(Integer),

    def __repr__(self):
        return f"{self.title}"


class Show(Base):
    __tablename__ = "show"
    gid = Column(Integer)
    id = Column(Integer, primary_key=True, unique=True)
    title = Column(String, unique=True)
    start_date = Column(Date, default=None)
    end_date = Column(Date, default=None)
    slug = Column(String, unique=True)

    # show.slug is the show's title with all punctuation & non-alphanumeric chars removed

    episodes = relationship("Episode")

    def __repr__(self):
        return f"{self.title}"

    def get_episodes(self, db_session):
        self.episodes = db_session.query(Episode).where(Episode.show_id == self.id)
