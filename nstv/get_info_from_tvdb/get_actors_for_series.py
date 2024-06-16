import os
from pprint import pprint

import requests
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


def download_image(character):
    image_url = character['image']
    if not image_url:
        image_url = character['personImgURL']
    r = requests.get(image_url)
    if r.status_code == 200:
        new_image_path = os.path.join(settings.STATIC_DIR + '/cast_members/', os.path.basename(image_url)).replace('\\', '/')
        with open(new_image_path, 'wb') as f:
            f.write(r.content)
        new_image_path = 'nstv' + new_image_path.split('/nstv/templates')[-1]
        return new_image_path
    else:
        print('Failed to download image: {}'.format(image_url))
        return None


def add_cast_members_for_series(series_id):
    show = Show.objects.get(tvdb_id=series_id)
    print('show: {}'.format(show))
    characters = tvdb.get_series_extended(series_id)['characters']
    for character in characters:
        #pprint(character)
        cast_member = CastMember.objects.filter(name=character['personName']).first()
        if not cast_member:
            image_url = download_image(character)
            cast_member = CastMember(
                name=character['personName'],
                image_url=image_url,
            )
            cast_member.shows.add(show)
            cast_member.save()
        if not cast_member.image_url:
            print('No image for cast member: {}'.format(cast_member))
            continue
        elif cast_member.image_url.startswith('https://artworks.thetvdb.com'):
            # old cast member image that needs to be replaced w/ local image path
            print('Old cast member image: {}'.format(cast_member.image_url))
            image_url = download_image(character)
            cast_member.image_url = image_url
            cast_member.save()
        elif cast_member.image_url.startswith('C:/'):
            # old cast member image that needs to be replaced w/ local image path
            print('Old cast member image: {}'.format(cast_member.image_url))
            image_url = download_image(character)
            cast_member.image_url = image_url
            cast_member.save()
        else:
            print('cast member already exists: {}, {}'.format(cast_member, cast_member.image_url))


if __name__ == '__main__':
    main()
