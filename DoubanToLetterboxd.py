import requests
from bs4 import BeautifulSoup
from requests.api import head
from tqdm import tqdm
import re
import csv
import time
import os

sleepTime = 2
beginPage = 0
endPage = 39
fav_url = ''
cookie = ''

def getItemList(session, payload):
    url = fav_url
    r = session.get(url, params=payload)
    bs = BeautifulSoup(r.content, 'lxml')
    href_list = bs.find_all('a', 'nbg')
    item_list = []
    for item in href_list:
        item_list.append(item['href'])
    return item_list

def getItemData(session, url): 
    r = session.get(url, headers=headers)
    bs = BeautifulSoup(r.content, 'lxml')
    info = bs.find(id='info')
    imdb = str(info.contents)
    imdb_pattern = 'tt\d+'
    imdb_result = re.findall(imdb_pattern, imdb)
    if imdb_result:
        imdb = imdb_result[0]
    else:
        imdb = ''
    colletion_date = bs.find('span', 'collection_date').string
    tag_html = bs.find('span', 'color_gray')
    tag_str = ''
    if tag_html != None and tag_html:
        tag_str = tag_html.string
      
    tag_list = tag_str.replace('标签:', '').split(' ')
    pattern = '^\d{1,2}$'
    prog = re.compile(pattern)
    rate = ''
    for tag in tag_list:
        if prog.match(tag):
            rate = tag

    double_rate = {'1':'2', '2': '4', '3':'6', '4':'8', '5':'10', '':''}
    if rate == '':
        rate_word = bs.find(id='n_rating')
        rate = double_rate[rate_word['value']]
    title = bs.find(attrs={'property': 'v:itemreviewed'}).string
    dataList = []
    dataList.append(imdb)
    dataList.append(title)
    dataList.append(rate)
    dataList.append(colletion_date)
    return dataList

def writeDataToCsv(dataList):
    with open('douban.csv', 'a', newline='', encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile)
        for data in dataList:
            spamwriter.writerow(data)

if __name__ == '__main__':
    if not os.path.exists('douban.csv'):
        with open('douban.csv', 'w', newline='', encoding='utf-8') as csvfile:
            spamwriter = csv.writer(csvfile)
            spamwriter.writerow(['imdbID','Title','Rating10','WatchedDate'])

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Accept-Encoding': 'gzip',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Cookie': cookie,
    }
    list_payload = {
        'start':'0',
        'sort':'time',
        'rating':'all',
        'filter':'all',
        'mode':'grid'
    }
    session = requests.Session()
    session.headers.update(headers)
    for page in range(beginPage, endPage):
        time.sleep(sleepTime)
        list_payload['start'] = str(page*15)
        page = page+1
        itemList = getItemList(session, list_payload)
        itemDataList = []
        for item in tqdm(itemList, desc=f"page {page}"):
            time.sleep(sleepTime)
            itemData = getItemData(session, item)
            itemDataList.append(itemData)
        print(itemDataList)
        writeDataToCsv(itemDataList)
    



    
