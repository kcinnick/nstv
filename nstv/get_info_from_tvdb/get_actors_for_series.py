import os
from pprint import pprint
import tvdb_v4_official
from django.conf import settings
from django import setup
from tqdm import tqdm

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
setup()

from nstv.models import CastMember, Show

tvdb = tvdb_v4_official.TVDB(os.getenv('TVDB_API_KEY'))

try:
    settings.configure()
except RuntimeError:  # settings already configured
    pass


def main():
    # series_id = 85019  # chopped
    for series in tqdm(Show.objects.all()):
        print('---')
        print('series: {}'.format(series))
        series_id = series.tvdb_id
        if series_id:
            add_cast_members_for_series(series_id)


def add_cast_members_for_series(series_id):
    show = Show.objects.get(tvdb_id=series_id)
    characters = tvdb.get_series_extended(series_id)['characters']
    for character in characters:
        #pprint(character)
        cast_member = CastMember.objects.filter(name=character['personName']).first()
        if not cast_member:
            image_url = character['image']
            if not image_url:
                image_url = character['personImgURL']
            cast_member = CastMember(
                name=character['personName'],
                image_url=image_url,
            )
            cast_member.save()
        cast_member.shows.add(show)
        cast_member.save()


if __name__ == '__main__':
    main()
