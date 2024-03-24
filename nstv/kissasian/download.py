# 1. import and build selenium browser
# 2. login to kissasian
# 3. go to show page and download episodes one after another
import os
from os import getenv
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm


def login():
    options = webdriver.ChromeOptions()

    chrome_prefs = {}
    options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"javascript": 2}
    chrome_prefs["profile.managed_default_content_settings"] = {"javascript": 2}

    chrome = webdriver.Chrome(options=options)
    sleep(5)
    chrome.get('https://kissasian.lu/Login')
    sleep(5)
    if chrome.current_url == 'https://kissasian.lu/Login':
        print('on login page')
    else:
        chrome.get('https://kissasian.lu/Login')
        sleep(5)
        print('on login page2')

    # wait until element is clickable
    element = WebDriverWait(chrome, 20).until(
        EC.element_to_be_clickable((By.ID, "username")))

    element.send_keys(getenv('KISSASIAN_USERNAME'))

    element = WebDriverWait(chrome, 20).until(
        EC.element_to_be_clickable((By.ID, "password")))

    element.send_keys(getenv('KISSASIAN_PASSWORD'))

    chrome.find_element('id', 'btnSubmit').click()
    sleep(1)

    return chrome


def get_episode_links(logged_in_session, show_url):
    tds = logged_in_session.find_elements(By.CLASS_NAME, "episodeSub")
    episode_links = []
    for td in tds:
        episode_links.append(td.find_element(By.TAG_NAME, "a").get_attribute('href'))

    return episode_links


def download_video_from_vidmoly(logged_in_session, video_dl_url, video_id):
    logged_in_session.get(video_dl_url)
    print('got video download page')
    sleep(5)
    logged_in_session.find_element(By.XPATH,
                                   '/html/body/div/div/div[3]/div/div/div[3]/div[2]/table/tbody/tr/td[1]/form/div/button').click()
    print('clicked download button')
    # poll downloads folder until video ID is found
    files_in_download_filder = list(reversed(os.listdir(getenv('DOWNLOADS_FOLDER'))))
    while f'{video_id}.mp4' not in files_in_download_filder:
        sleep(30)
        files_in_download_filder = os.listdir(getenv('DOWNLOADS_FOLDER'))
        print('waiting..')

    return


def main():
    # episode_numbers = ['94', '95', '96', '97', '98', '99', '100']
    episode_numbers = [str(i) for i in range(82, 120)]
    logged_in_session = login()
    print('Login to vidmoly.')
    logged_in_session.get('https://vidmoly.me/login.html')
    print('got vidmoly login page')
    input('Press enter after logging in to vidmoly.')
    sleep(5)
    print('logged in to both sites.')
    for episode_number in tqdm(episode_numbers):
        episode_to_download = f'Episode-{episode_number}'
        if len(episode_number) == 1:
            episode_number = f'00{episode_number}'
        elif len(episode_number) == 2:
            episode_number = f'0{episode_number}'
        else:
            pass
        new_file_name = f'Running.Man.S01.E{episode_number}.720P.mp4'
        show_url = 'https://kissasian.lu/Drama/Running-Man-Game-Show'
        logged_in_session.get(show_url)
        print('got show page')
        sleep(5)
        episode_links = get_episode_links(logged_in_session, show_url)
        print('got episode links')
        for episode_link in episode_links:
            if episode_to_download not in episode_link:
                continue
            logged_in_session.get(episode_link)
            print('got episode page')
            video_source = logged_in_session.find_element(By.ID, 'my_video_1').get_attribute('src')
            video_id = video_source.split('/')[-1].split('.')[0].replace('embed-', '')
            video_dl_url = f'https://vidmoly.me/dl/{video_id}'
            download_video_from_vidmoly(logged_in_session, video_dl_url, video_id)
            print(f'found {video_id}.mp4. Download finished.')
            # rename file to episode number
            os.rename(f'{getenv("DOWNLOADS_FOLDER")}/{video_id}.mp4', f'{getenv("DOWNLOADS_FOLDER")}/{new_file_name}')
            #input('Press enter to continue to next episode.')
            sleep(10)
            print('continuing to next episode.')


if __name__ == '__main__':
    main()
