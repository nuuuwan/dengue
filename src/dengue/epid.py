"""Dengue."""
import os

from bs4 import BeautifulSoup
from utils import dt, jsonx, timex, www

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
        row = list(
            map(
                lambda td: td.text.strip(),
                tr.find_all('td'),
            )
        )
        if not row:
            continue
        rdhs_name = row[0]
        if rdhs_name == 'TOTAL':
            continue
        data_by_month = list(map(dt.parse_int, row[1:13]))
        data_list.append(
            {
                'rdhs_name': rdhs_name,
                'district_id': _rdhs_to_district(rdhs_name),
                'data_by_month': data_by_month,
            }
        )
    date_id = timex.get_date_id()
    data_file = '/tmp/dengue.%s.json' % (date_id)
    jsonx.write(data_file, data_list)
    log.info('Wrote data to %s', data_file)


def _dump_summary():
    MAX_MISSING_DAYS = 5
    ut = timex.get_unixtime()
    missing_days = 0
    all_data_list = []
    while missing_days < MAX_MISSING_DAYS:
        date_id = timex.get_date_id(ut)
        data_file = '/tmp/dengue.%s.json' % (date_id)

        data_list = None
        if os.path.exists(data_file):
            data_list = jsonx.read(data_file)
        else:
            url = os.path.join(
                'https://raw.githubusercontent.com/nuuuwan/dengue',
                'data/dengue.%s.json' % date_id,
            )
            if www.exists(url):
                data_list = www.read_json(url)
                jsonx.write(data_file, data_list)
            else:
                missing_days += 1
        all_data_list.append(
            {
                'date_id': date_id,
                'data_list': data_list,
            }
        )

        if data_list:
            log.info('Loaded data for %s', date_id)
        else:
            log.warn('No data for %s', date_id)

        ut -= timex.SECONDS_IN.DAY

    all_data_list = sorted(
        all_data_list,
        key=lambda d: d['date_id'],
    )

    # summarize
    timeseries = []
    prev_item = None
    for all_data in all_data_list:
        date_id = all_data['date_id']
        ut = timex.parse_time(date_id, '%Y%m%d')
        date = timex.format_time(ut, '%Y-%m-%d')

        data_list = all_data['data_list']
        if data_list is not None:
            by_rhds = []
            total_cum_cases = 0
            for d in data_list:
                cum_cases = sum(d['data_by_month'])
                by_rhds.append(
                    {
                        'rdhs_name': d['rdhs_name'],
                        'district_id': d['district_id'],
                        'cum_cases': cum_cases,
                    }
                )
                total_cum_cases += cum_cases
            by_rhds = sorted(
                by_rhds,
                key=lambda for_rdhs: for_rdhs['district_id']
                + for_rdhs['rdhs_name'],
            )

            item = {
                'date': date,
                'ut': ut,
                'by_rhds': by_rhds,
                'total_cum_cases': total_cum_cases,
            }
        else:
            if prev_item is not None:
                item = {
                    'date': date,
                    'ut': ut,
                    'by_rhds': prev_item['by_rhds'],
                    'total_cum_cases': prev_item['total_cum_cases'],
                }
            else:
                continue

        timeseries.append(item)
        prev_item = item

    extended_timeseries = []
    prev_item = None
    for item in timeseries:
        item['total_new_cases'] = item['total_cum_cases']
        if prev_item:
            item['total_new_cases'] -= prev_item['total_cum_cases']

        extended_by_rdhs = []
        for i, for_rdhs in enumerate(item['by_rhds']):
            for_rdhs['new_cases'] = for_rdhs['cum_cases']

            if prev_item:
                for_rdhs['new_cases'] -= prev_item['by_rhds'][i]['cum_cases']
            extended_by_rdhs.append(for_rdhs)
        item['by_rhds'] = extended_by_rdhs

        extended_timeseries.append(item)
        prev_item = item

    summary_data_file = '/tmp/dengue.summary.latest.json'
    jsonx.write(summary_data_file, extended_timeseries)
    log.info('Wrote summary to %s', summary_data_file)


if __name__ == '__main__':
    _dump_summary()
