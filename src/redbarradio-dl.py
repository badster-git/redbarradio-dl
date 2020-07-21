from bs4 import BeautifulSoup
from tabulate import tabulate
from settings import *
import re
import os
import youtube_dl
import requests

def getEpisodes():
    redbarRadio_url = "https://redbarradio.net/category/shows/"

    response = requests.get(redbarRadio_url)
    data = response.text
    soup = BeautifulSoup(data, 'lxml')
    episodes = soup.find_all('td', class_='col1 first')
    return episodes

def formatEpisodes(episodes):
    episodeLinks = []
    fmtEpisodes = []
    cntEpisode = 1
    for rawEpisode in episodes:
        fullEpisodeName = rawEpisode.find('a').text

        if ('RED BAR RADIO' in fullEpisodeName):
            episodeSeasonNumber = fullEpisodeName.split()[-2:-1]
            episodeNumber = fullEpisodeName.split()[-1]
            episodeName = ((fullEpisodeName.rsplit(" ", 2)[0]) + ' ' + episodeNumber)

            if (not rawEpisode.a.attrs['href'].endswith(('-2', '-3'))):
                link = rawEpisode.a.attrs['href']
                episode = (cntEpisode, episodeSeasonNumber[0], episodeName)
                linkList = {'name': episodeName, 'link': link}

                episodeLinks.append(linkList)
                fmtEpisodes.append(episode)
                cntEpisode += 1
                nEpisodes = len(episodeLinks)
    return(fmtEpisodes, episodeLinks, nEpisodes)

def selectEpisode(episodes, links, nEpisodes):
    headers = ['#', 'Season', 'Episode']
    print(tabulate(episodes[0:nEpisodes], headers))

    noMoreMatches = nEpisodes == len(episodes)

    if noMoreMatches:
        print('\nEND OF LIST. NO MORE EPISODES FOUND')

    while True:
        if noMoreMatches:
            elec = input('Type # of episode to download or q to quit: ')
        dashFormat = re.search("\d+\-\d+", elec)
        commaFormat = re.search("\d+\,\d+", elec)
        if elec.isnumeric():
            choice = int(elec) - 1
            if choice < len(episodes) and choice >= 0:
                title = '{}.mp4'.format(links[choice]['name'], episodes[choice][-2])
                downloadVideo(links[choice]['link'])
            else:
                print("Couldn't fetch the episode #{}".format(str(choice + 1)))
                continue
        elif dashFormat:
            first, last = int(elec.rsplit('-', 1)[0]) - 1, int(elec.rsplit('-', 1)[1]) - 1
            if((first < last) and (first >= 0) and (last >= 0) and (first != last) and (last < len(episodes))):
                for i in range(first, last):
                    downloadVideo(links[i]['link'])
            else:
                print("Couldn't fetch episodes #{}-{}".format(str(first + 1), str(last + 1)))
                continue
        elif commaFormat:
            listOfEps = elec.split(',')
            for i in range(len(listOfEps)):
                choice = int(listOfEps[i]) - 1
                if choice >= 0 and choice < len(episodes):
                    downloadVideo(links[choice]['link'])
                else:
                    print('Not a valid option.')
                    continue
        elif(elec.lower() == 'q'):
            return False
        elif not elec:
            if noMoreMatches:
                print('Not a valid option.')
                continue
            else:
                return True
        else:
            print('Not a valid option.')

def downloadVideo(link):
    try:
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)
        os.makedirs(ARCHIVE_PATH, exist_ok=True)
        FILENAME = DOWNLOAD_PATH + '/%(title)s.%(ext)s'
        ARCHIVE_FILE = ARCHIVE_PATH + "/archive.txt"
        ydl_opts = {
            'outtmpl': FILENAME,
            'download_archive': ARCHIVE_FILE,
            'format': 'mp4',
            'restrictfilenames': True,
            'no_warnings': True,
            'quiet': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            vidInfo = ydl.extract_info(link, download = False)

            if not ydl.in_download_archive(vidInfo):
                print('Downloading...')
                ydl.download([link])
                ydl.record_download_archive(vidInfo)
                print('Video downloaded to {}'.format(DOWNLOAD_PATH))
            else:
                print('Video has already been downloaded.')
    except (youtube_dl.utils.ExtractorError, youtube_dl.utils.DownloadError) as e:
            print(f"Error when interacting with youtube, skipping: {e}")

def main():
    episodes = []
    links = []
    newEpisodes, newLinks, nEpisodes = formatEpisodes(getEpisodes())
    episodes += newEpisodes
    links += newLinks
    selectEpisode(episodes, links, nEpisodes)


if __name__ == '__main__':
    main()
