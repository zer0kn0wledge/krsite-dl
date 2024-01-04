import datetime
import time
import json
import re

from rich import print
from common.common_modules import SiteRequests
from common.data_structure import Site, ScrapperPayload

SITE_INFO = Site(hostname="programs.sbs.co.kr", name="SBS Program", location="KR")

def get_data(hd):
    site_req = SiteRequests()
    board_no = hd.split('board_no=')[-1].split('&')[0]
    parent_name = re.search(r'(?:(https|http)://)?(programs\.sbs\.co\.kr)(?:/[^/]+){1}/([^/?]+)', hd).group(3)
    vis_board_no = re.search(r'(?:(https|http)://)?(programs\.sbs\.co\.kr)(?:/[^/]+){3}/([^/?]+)', hd).group(3)
    print(f"Board no: {board_no}")

    menu_api = "https://static.apis.sbs.co.kr/program-api/1.0/menu/"

    menu_r = site_req.session.get(menu_api + parent_name).json()['menus']

    all_board = []
    for menu in menu_r:
        if menu['board_code'] is not None:
            menu_id = menu['mnuid']
            board_code = menu['board_code'].split(',')
            all_board.append({menu_id: board_code})
            if menu['submenus']:
                for submenu in menu['submenus']:
                    if submenu['board_code'] is not None:
                        menu_id = submenu['mnuid']
                        board_code = submenu['board_code'].split(',')
                        all_board.append({menu_id: board_code})

    code_temp = [] 

    for i in all_board:
        for key, value in i.items():
            if key == vis_board_no:
                for j in value:
                    code_temp.append(j.strip())

    ###########TOKEN############
    current_milli_time = int(round(time.time() * 1000))
    token = str(current_milli_time)
    ############################

    code = ''

    for i in code_temp:
        # print(f"[green]Code:[/green] {i}")
        code = i
        api = f"https://api.board.sbs.co.kr/bbs/V2.0/basic/board/detail/{board_no}"

        params = {
            'callback': f'boardViewCallback_{code}',
            'action_type': 'callback',
            'board_code': code,
            'jwt-token': '',
            '_': token
        }
    
        r = site_req.session.get(api, params=params)

        if 'err_code' not in r.text:
            break

    json_data = r.text
    json_data = json_data.split('boardViewCallback_%s(' % code)[1]
    json_data = json_data.rstrip(');')
    json_data = json.loads(json_data)
    
    data = json_data['Response_Data_For_Detail']
    post_title = data['TITLE'].strip()
    post_date = data['REG_DATE'].strip()
    post_date = datetime.datetime.strptime(post_date, '%Y-%m-%d %H:%M:%S')
    post_date_short = post_date.strftime('%y%m%d')

    img_list = set()

    print(f"Title: {post_title}")
    print(f"Date: {post_date}")

    for i in data['URL']:
        if 'http' not in i:
            img_list.add('http:' + str(i))
        else:
            img_list.add(str(i))
    
    print(f"Found {len(img_list)} image(s)")

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