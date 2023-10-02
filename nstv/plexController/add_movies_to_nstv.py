import os

import django
from plexapi.myplex import MyPlexAccount

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()
from nstv.models import Movie

account = MyPlexAccount('nicktucker4@gmail.com', os.getenv('PLEX_API_KEY'))
plex = account.resource(os.getenv('PLEX_SERVER')).connect()  # returns a PlexServer instance


def add_movies_to_nstv():
    plex_movies = plex.library.section('Movies')
    for movie in plex_movies.search():
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
        else:
            print('movie does not exist')
            movie_object = Movie(
                title=movie.title, release_date=movie.originallyAvailableAt, genre=movie.genres,
                director=movie.directors[0], on_disk=True
            )
            movie_object.save()
            print('movie added to database')

    return


def main():
    add_movies_to_nstv()
    return


if __name__ == '__main__':
    main()
