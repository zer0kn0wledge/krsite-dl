import datetime
import json
import re

from pytz import timezone
from urllib.parse import urlparse, urlunparse
from common.common_modules import SiteRequests, SiteParser
from common.data_structure import Site, ScrapperPayload

SITE_INFO = Site(hostname="nonno.hpplus.jp", name="Non-no", location="JP")

def get_data(hd):
    site_parser = SiteParser()
    site_requests = SiteRequests()
    soup = site_parser._parse(site_requests.session.get(hd).text)


    # article info
    info = (soup.find_all('script', type='application/ld+json')[2])
    info = json.loads(info.string)

    post_title = info['headline']
    post_date = datetime.datetime.strptime(info['datePublished'], '%Y-%m-%dT%H:%M:%S%z')
    post_date_short = post_date.strftime('%y%m%d')
    tz = timezone('Asia/Seoul')
    post_date = post_date.astimezone(tz).replace(tzinfo=None)


    contents = soup.find_all('figure')

    img_list = []
    for content in contents:
        img = content.find('img')
        url_parts = urlparse(img['src'])
        new_url_parts = url_parts._replace(query=None, path=re.sub(r'/q=\d+,\w+=\w+:\w+', '', url_parts.path))
        img_url = urlunparse(new_url_parts)
        img_list.append(img_url)

    print("Title: %s" % post_title)
    print("Date: %s" % post_date)
    print("Found: %s image(s)" % len(img_list))

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