from datetime import datetime
from pprint import pprint

from helper import get_start_of_month, get_end_of_day, generate_event_path

months = {
    '01': 'January',
    '02': 'February',
    '03': 'March',
    '04': 'April',
    '05': 'May',
    '06': 'June',
    '07': 'July',
    '08': 'August',
    '09': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December',
}

event_type_class_map = {
    'Global Day': 'event--highlighted',
    'Regional Day': 'event--highlighted'
}

iso_label_dict = {
    'AT': 'Austria',
    'BE': 'Belgium',
    'BG': 'Bulgaria',
    'BY': 'Belarus',
    'CH': 'Switzerland',
    'CZ': 'Czech Republic',
    'DE': 'Germany',
    'DK': 'Denmark',
    'ES': 'Spain',
    'FR': 'France',
    'GR': 'Greece',
    'HR': 'Croatia',
    'HU': 'Hungary',
    'IE': 'Ireland',
    'IT': 'Italy',
    'KO': 'Kosova',
    'NL': 'the Netherlands',
    'NO': 'Norway',
    'PL': 'Poland',
    'PT': 'Portugal',
    'RO': 'Romania',
    'RS': 'Serbia',
    'SE': 'Sweden',
    'SQ': 'Albania',
    'UA': 'Ukraine',
    'UK': 'United Kingdom'
}


def parse_events(reader, today, approved):

    all_events = []
    upcoming = {}
    prev = {}

    for month_key, month in months.items():
        upcoming[month_key] = {
            'label': month,
            'events': []
        }
        prev[month_key] = {
            'label': month,
            'events': []
        }

    for row in reader:

        if not approved and row['approved'] != 'yes':
            continue

        event = parse_event(row, today)

        if event is None:
            continue

        all_events.append(event)
        start_month = event['start_month']

        if event['upcoming']:
            upcoming[start_month]['events'].append(event)
        else:
            prev[start_month]['events'].append(event)

    for month_key,month in upcoming.items():
        month['events'] = sorted(month['events'], key=lambda event: event['start_day'])

    for month_key,month in prev.items():
        month['events'] = sorted(month['events'], key=lambda event: event['start_day'])

    return {
        'all': all_events,
        'upcoming': upcoming,
        'prev': prev
    }


def parse_event(row, today):

    start_of_month = get_start_of_month(today)
    end_of_today = get_end_of_day(today)

    try:
        start_date = datetime.strptime(row['datestart'], '%Y%m%d')
    except ValueError:
        pprint('error parsing datestart')
        pprint(row)
        return None

    start_day = start_date.strftime('%d')
    start_month = start_date.strftime('%m')
    start_year = start_date.strftime('%Y')

    end_date = datetime.strptime(row['dateend'], '%Y%m%d')
    end_day = end_date.strftime('%d')

    upcoming_event = start_date > start_of_month

    classes = event_type_class_map.get(row['type'], '')

    if row['coclink'] and row['coclink'] != 'nococ':
        coc_link = row['coclink']
    else:
        coc_link = None

    if row['city'] == '--' or not row['city']:
        city = ''
    else:
        city = row['city']

    if row['country'] == '--' or not row['country']:
        country = ''
    else:
        country_code = row['country'].strip()
        country = iso_label_dict.get(country_code, country_code)

    if upcoming_event:
        cfp_link = row['cfplink']

        if row['cfpdate']:
            if row['cfpdate'] == 'open':
                cfp_date = None
            else:
                try:
                    cfp_date = datetime.strptime(row['cfpdate'], '%Y%m%d')

                    if cfp_date < end_of_today:
                        cfp_date = None
                        cfp_link = None
                except:
                    cfp_date = None

        else:
            cfp_date = None
    else:
        cfp_date = None
        cfp_link = None

    if cfp_link == '--' or cfp_link == 'nada':
        cfp_date = None
        cfp_link = None

    if row['EntranceFee'] != '0':
        fee = row['EntranceFee']
    else:
        fee = None

    if row['Registration'] and row['Registration'] != 'no':
        reg = True
        if row['Registration'] != 'no':
            reg_link = row['Registration']
        else:
            reg_link = None
    else:
        reg = False
        reg_link = None

    try:
        lat = float(row['lat'])
        lon = float(row['lon'])
        geo = 'geo:' + str(lat) + ',' + str(lon)
    except:
        lat = None
        lon = None
        geo = None

    event = {
        'label': row['label'],
        'description': row['Self-description'],
        'start_day': start_day,
        'start_month': start_month,
        'start_month_string': months[start_month],
        'start_year': start_year,
        'end_day': end_day,
        'homepage': row['homepage'],
        'fee': fee,
        'venue': row['venue'],
        'city': city,
        'country': country,
        'osm_link': row['OSM-Link'],
        'geo': geo,
        'cfp_date': cfp_date,
        'cfp_link': cfp_link,
        'coc_link': coc_link,
        'reg': reg,
        'reg_link': reg_link,
        'classes': classes,
        'type': row['type'],
        'upcoming': upcoming_event,
        'participants': row['ParticipantsLastTime'],
        'lat': lat,
        'lon': lon
    }

    event['details_url'] = generate_event_path(event)

    return event
