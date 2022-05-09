import sqlite3
from urllib.request import urlopen
from urllib.error import HTTPError
import json
import re
from tqdm import tqdm

con = sqlite3.connect('subtitles.db')

cur = con.cursor()

# create table
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()

if not tables or ('subtitles' not in tables[0]):
    cur.execute(
        '''
        CREATE TABLE subtitles
        (videoId integer, duration integer, content text, startOfParagraph integer, startTime integer, videoLink text, videoName text, videoAge integer, videoLocation text, videoLength integer)
        ''')

# Поиск необходимой информации и субтитров к видео
def parse_video_subtitles(videoId, lang):
    try:
        ted_url = urlopen(f'https://www.ted.com/talks/subtitles/id/{videoId}/lang/{lang}')
    except HTTPError: return None
    try:
        ted_url1 = urlopen(f'https://www.ted.com/talks/{videoId}')
    except HTTPError: return None

    ted_json = ted_url.read().decode('utf8')
    ted_list = json.loads(ted_json)

    ted_json1 = ted_url1.read().decode('utf8')

    rows = []
    videoLink = re.search(r'[^\"]+(py\.tedcdn)[^\"\\]+', ted_json1)[0]
    videoName = re.search(r'(text\-tui\-4xl mr\-5\"\>)([^\<])+', ted_json1)[0][19:]
    videoLocation = re.search(r'\"video\-context\"\>TE[^\d]+', ted_json1)[0][16:]
    videoAge = int(videoLink[60:64])
    videoLength = (ted_list['captions'][len(ted_list['captions'])-1]['startTime'] + ted_list['captions'][len(ted_list['captions'])-1]['duration']) // 1000
    for i in ted_list['captions']:
        rows.append([
            videoId,
            i['duration'],
            i['content'],
            i['startOfParagraph'],
            i['startTime'],
            videoLink,
            videoName,
            videoAge,
            videoLocation,
            videoLength])
    cur.executemany('insert into subtitles values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', rows)


for videoId in tqdm(range(1,1001)):
    parse_video_subtitles(videoId, 'en')

con.commit()

con.close()
