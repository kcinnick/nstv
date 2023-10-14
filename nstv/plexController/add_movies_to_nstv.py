import os

import django
from plexapi.myplex import MyPlexAccount
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()
from nstv.models import Movie

account = MyPlexAccount('nicktucker4@gmail.com', os.getenv('PLEX_API_KEY'))
plex = account.resource(os.getenv('PLEX_SERVER')).connect()  # returns a PlexServer instance


def save_movie_poster(plex_movie):
    posterUrl = plex_movie.posterUrl

    if posterUrl:
        posterSavePath = os.path.join(r'C:\Users\Nick\PycharmProjects\djangoProject\nstv\static' + '\\images\\posters',  plex_movie.title.replace(' ', '_') + '.jpg')
        if not os.path.exists(posterSavePath):
            r = requests.get(posterUrl, allow_redirects=True)
            with open(posterSavePath, 'wb') as f:
                f.write(r.content)
    else:
        posterSavePath = None

    return posterSavePath


def add_movies_to_nstv():
    plex_movies = plex.library.section('Movies')
    for movie in plex_movies.search():
        posterPath = save_movie_poster(movie)
        movie_object = Movie.objects.all().filter(title=movie.title)
        if movie_object:
            print('movie already exists')
            # add missing movie details if any
            if not movie_object[0].genre:
                movie_object[0].genre = movie.genres
                movie_object[0].save()
                print('genre added to movie')
            if not movie_object[0].director:
                movie_object[0].director = movie.directors[0]
                movie_object[0].save()
                print('director added to movie')
            if not movie_object[0].on_disk:
                movie_object[0].on_disk = True
                movie_object[0].save()
                print('on_disk added to movie')
            if not movie_object[0].release_date:
                movie_object[0].release_date = movie.originallyAvailableAt
                movie_object[0].save()
                print('release_date added to movie')
            if not movie_object[0].poster_path:
                movie_object[0].poster_path = posterPath
                movie_object[0].save()
                print('poster_path added to movie')
        else:
            print('movie does not exist')
            movie_object = Movie(
                title=movie.title, release_date=movie.originallyAvailableAt, genre=movie.genres,
                director=movie.directors[0], on_disk=True, poster_path=posterPath
            )
            movie_object.save()
            print('movie added to database')

    return


def main():
    add_movies_to_nstv()
    return


if __name__ == '__main__':
    main()
