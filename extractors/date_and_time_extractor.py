from base_extractor import BaseExtractor
import parsedatetime as pdt
from email.utils import parsedate
import re

def validate_date(date, context):
  date_text = date[-1]
  if any([date_text in x for x in context['original_links']]):
    return False
  matches = re.search(r'(\d{1,2})[\.:]\d{1,2}|(\d{1,2})\s?(am|pm|AM|PM)', date_text)
  if matches:
    if (matches.group(1) and matches.group(1) > 12) or (matches.group(2) and matches.group(2) > 12):
      return False
  if "\n" in date_text:
    return False
  if len(date_text) < 5 and not any([x in date_text for x in ['-', '/', 'am', 'pm']]):
    return False
  return not date_text.isdigit() and not date_text.startswith('--') and any([x in date_text for x in [' ', '-', '/']])

class DateAndTimeExtractor(BaseExtractor):
    @staticmethod
    def extract(message, context):
      body = message.get('payload').get('body')
      cal = pdt.Calendar()
      date_header = message.get_header('Date')
      if not date_header:
        DateAndTimeExtractor.throw()
      start_date = parsedate(date_header)
      dates = cal.nlp(body, sourceTime=start_date)
      if dates:
        dates = list(filter(lambda x: validate_date(x, context), dates))
        dates.sort(key=lambda x: len(x[-1]))
        for date in dates:
          if date[-1][0].isdigit():
            return {'datetime': date}, {}
        for date in dates:
          if date[-1][0].isupper():
            return {'datetime': date}, {}
        for date in dates:
          if date[-1][0] not in ['tonight', 'today', 'tomorrow']:
            return {'datetime': date}, {}
        if dates:
          return {'datetime': dates[0]}, {}
        DateAndTimeExtractor.throw()
      else:
        DateAndTimeExtractor.throw()

