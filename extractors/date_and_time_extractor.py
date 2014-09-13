from base_extractor import BaseExtractor
import parsedatetime as pdt
from email.utils import parsedate

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
      if dates and not dates[0][-1].isdigit() and not dates[0].startswith('--') and any([x in dates[0] for x in [' ', '-', '/']]):
        return {'datetime': dates[0]}, {}
      else:
        DateAndTimeExtractor.throw()

