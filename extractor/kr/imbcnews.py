import datetime
import re

from common.common_modules import SiteRequests, SiteParser
from common.data_structure import Site, ScrapperPayload

SITE_INFO = Site(hostname="enews.imbc.com", name="iMBC News", location="KR")

def get_data(hd):
    site_parser = SiteParser()
    site_requests = SiteRequests()
    soup = site_parser._parse(site_requests.session.get(hd).text)

    post_title = soup.find('h2').text.strip()
    post_date = soup.find('span', class_='date').text.strip()
    post_date_short = post_date.replace('-', '')
    post_date_short = re.sub('[\u3131-\uD7A3]+', '', post_date_short)[2:8]

    img_list = []

    for item in soup.findAll('img'):
        if item.get('src') is not None:
            if 'talkimg.imbc.com' in item.get('src'):
                img_list.append('http:' + item.get('src'))
    
    print("Found %s image(s)" % len(img_list))

    post_date = re.sub('[\u3131-\uD7A3]+', '', post_date)
    post_date = datetime.datetime.strptime(post_date, '%Y-%m-%d %H:%M')

    print("Title: %s" % post_title)
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

    DirectoryHandler().handle_directory_alternate(payload)