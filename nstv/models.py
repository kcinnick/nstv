from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Show(Base):
    __tablename__ = "shows"

    id = Column(Integer, primary_key=True, unique=True)
    title = Column(String, unique=True)
    start_date = Column(Date, default=None)
    end_date = Column(Date, default=None)
    # show.slug is the show's title with all punctuation & non-alphanumeric chars removed
    slug = Column(String, unique=True)

    episode = relationship("Episode")

    def __repr__(self):
        return f"{self.title}"


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, unique=True)
    show = Column(String, ForeignKey("shows.slug"))
    # episode.slug is the episode's title with all punctuation & non-alphanumeric chars removed
    air_date = Column(Date)
    title = Column(String)
    slug = Column(String)

    show_ = relationship("Show")

    def __repr__(self):
        return f"{self.title}"
