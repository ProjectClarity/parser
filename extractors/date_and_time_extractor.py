from base_extractor import BaseExtractor
import parsedatetime as pdt
from email.utils import parsedate

def validate_date(date):
  return not date[-1].isdigit() and not date[-1].startswith('--') and any([x in date[-1] for x in [' ', '-', '/']])

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
        dates = filter(lambda x: validate_date(x), dates)
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

