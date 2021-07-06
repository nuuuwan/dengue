"""Dengue."""
import os

from bs4 import BeautifulSoup

from utils import www, dt, timex, jsonx

from dengue._utils import log


RDHS_TO_DISTRCT = {
    'Colombo': 'LK-11',
    'Gampaha': 'LK-12',
    'Kalutara': 'LK-13',
    'Kandy': 'LK-21',
    'Matale': 'LK-22',
    'Nuwara Eliya': 'LK-23',
    'Galle': 'LK-31',
    'Hambantota': 'LK-33',
    'Matara': 'LK-32',
    'Jaffna': 'LK-41',
    'Kilinochchi': 'LK-45',
    'Mannar': 'LK-42',
    'Vavuniya': 'LK-43',
    'Mulativu': 'LK-44',
    'Batticaloa': 'LK-51',
    'Ampara': 'LK-52',
    'Trincomalee': 'LK-53',
    'Kurunegala': 'LK-61',
    'Puttalam': 'LK-62',
    'Anuradhapura': 'LK-71',
    'Polonnaruwa': 'LK-72',
    'Badulla': 'LK-81',
    'Moneragala': 'LK-82',
    'Ratnapura': 'LK-91',
    'Kegalle': 'LK-92',
    'Kalmunai': 'LK-52',
}


def _rdhs_to_district(rdhs_name):
    if rdhs_name in RDHS_TO_DISTRCT:
        return RDHS_TO_DISTRCT[rdhs_name]

    print("'%s': 'LK-11'," % rdhs_name)
    return ''


def _scrape_and_dump():
    URL = os.path.join(
        'http://www.epid.gov.lk/web/index.php?',
        'Itemid=448&lang=en&option=com_casesanddeaths',
    )
    html = www.read(URL)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='viewDeseases')

    data_list = []
    for tr in table.find_all('tr'):
        row = list(map(
            lambda td: td.text.strip(),
            tr.find_all('td'),
        ))
        if not row:
            continue
        rdhs_name = row[0]
        if rdhs_name == 'TOTAL':
            continue
        data_by_month = list(map(dt.parse_int, row[1:13]))
        data_list.append({
            'rdhs_name': rdhs_name,
            'district_id': _rdhs_to_district(rdhs_name),
            'data_by_month': data_by_month,
        })
    date_id = timex.get_date_id()
    data_file = '/tmp/dengue.%s.json' % (date_id)
    jsonx.write(data_file, data_list)
    log.info('Wrote data to %s', data_file)


if __name__ == '__main__':
    _scrape_and_dump()
