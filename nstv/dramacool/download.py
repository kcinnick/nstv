from pprint import pprint

import requests
from bs4 import BeautifulSoup

listings = {
    'Hometown Cha-Cha-Cha': 'https://ww8.dramacoool.co/watch/series/hometown-cha-cha-cha-2021/',
}


def get_episode_download_url(url, episode_number):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    episode_container = soup.find('ul', class_='list-episode-item-2 all-episode')
    urls = episode_container.find_all('a')
    for url in urls:
        if f'{episode_number}' == url.text.split('\n')[2].split()[-1]:
            episode_url = url['href']
            break
        else:
            print(url.text.split('\n')[2])
    response = session.get(episode_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    download_url = soup.find('li', class_='download').a['href']
    print(download_url)

    return download_url


def download_from_draplay(download_url):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})
    response = session.get(download_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    #print(soup.prettify())
    quit()


def main():
    show_name = 'Hometown Cha-Cha-Cha'
    url = listings[show_name]
    download_url = get_episode_download_url(url, 16)
    if 'draplay' in download_url:
        download_from_draplay(download_url)
    else:
        raise Exception('Unknown download url: {}'.format(download_url))


if __name__ == '__main__':
    main()
