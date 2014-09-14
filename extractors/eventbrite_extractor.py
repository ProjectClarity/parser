import re

import arrow
from bs4 import BeautifulSoup
import requests

from base_extractor import BaseExtractor

EVENTBRITE_EVENT_REGEX = r'eventbrite\.com\/e\/(?:[a-z0-9]+-)+(\d+)$'

def naive_datetime_from_span(dt_span, timezone):
    return arrow.get(dt_span.find("span")['title']).to(timezone).datetime.replace(tzinfo=None)

class EventbriteExtractor(BaseExtractor):
    @staticmethod
    def extract(message, context):
       for link in context['links']:
           match = re.search(EVENTBRITE_EVENT_REGEX, link)
           if match:
               event_page = requests.get(link)
               soup = BeautifulSoup(event_page.text)
               start = soup.find("span", class_="dtstart")
               end = soup.find("span", class_="dtend")
               timezone = message.get_header('X-Time-Zone')
               return {'eventbrite_url': link, 'datetime': naive_datetime_from_span(start, timezone), 'end': naive_datetime_from_span(end, timezone)}, {}
       return {}, {}
