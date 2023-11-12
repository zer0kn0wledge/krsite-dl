import requests
import datetime

from client.user_agent import InitUserAgent
from common.data_structure import Site, ScrapperPayload
from bs4 import BeautifulSoup

SITE_INFO = Site(hostname="dazedkorea.com", name="Dazed Korea", location="KR")

def get_data(hd):
    r = requests.get(hd, headers={'User-Agent': InitUserAgent().get_user_agent()})
    soup = BeautifulSoup(r.text, 'html.parser')

    post_title = soup.find('h1', class_='title').text.strip()
    post_summary = soup.find('h2', class_='summary').text.strip()
    post_title = post_title + ' ' + post_summary
    post_date = soup.find('time', class_='timestamp').text.strip()
    post_date_short = post_date.replace('/', '')[2:8]
    post_date = datetime.datetime.strptime(post_date, '%Y/%m/%d')
    content = soup.find('div', class_='article-body')

    img_list = []
    
    for item in content.findAll('img'):
        img_list.append('http://dazedkorea.com' + item.get('src'))

    print("Title: %s" % post_title)
    print("Summary: %s" % post_summary)
    print("Date: %s" % post_date)
    print("Found %s image(s)" % len(img_list))

    payload = ScrapperPayload(
        title=post_title,
        shortDate=post_date_short,
        mediaDate=post_date,
        site=SITE_INFO.name,
        series=None,
        writer=None,
        location=SITE_INFO.location,
        media=img_list,
    )

    from down.directory import DirectoryHandler

    DirectoryHandler().handle_directory(payload)