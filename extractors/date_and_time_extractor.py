from base_extractor import BaseExtractor
import parsedatetime as pdt
from email.utils import parsedate
import re

def validate_date(date, body, context):
  parsed_datetime, flags, start_pos, end_pos, date_text = date
  if any([date_text in x for x in context['original_links']]):
    return False
  if re.search(r'\s[A-Za-z]$', date_text):
    return False
  if re.search(r'\s\d{3,}$', date_text):
    return False
  if re.search(r'\d{3,}\s?(am|pm)$', date_text, re.IGNORECASE):
    return False
  matches = re.search(r'(\d{1,2})[\.:]\d{1,2}|(\d{1,2})\s?(am|pm)', date_text, re.IGNORECASE)
  if matches:
    if (matches.group(1) and int(matches.group(1)) > 12) or (matches.group(2) and int(matches.group(2)) > 12):
      return False
  if "\n" in date_text:
    return False
  if len(date_text) < 5 and not any([x in date_text.lower() for x in ['-', '/', 'am', 'pm']]):
    return False
  if date_text.isdigit():
    return False
  if date_text.startswith('--'):
    return False
  if not any([x in date_text for x in [' ', '-', '/']]):
    return False
  if any([x in body[end_pos+1:end_pos+5].lower() for x in ['am', 'pm']]):
    return False

  return True

class DateAndTimeExtractor(BaseExtractor):
    @staticmethod
    def extract(message, context):
      body = message.get('payload').get('body')
      cal = pdt.Calendar()
      date_header = message.get_header('Date')
      if not date_header:
        DateAndTimeExtractor.throw()
      start_date = parsedate(date_header)
      try:
        dates = cal.nlp(body, sourceTime=start_date)
      except:
        DateAndTimeExtractor.throw()
      if dates:
        dates = list(filter(lambda x: validate_date(x, body, context), dates))
        # dates.sort(key=lambda x: len(x[-1]))
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

