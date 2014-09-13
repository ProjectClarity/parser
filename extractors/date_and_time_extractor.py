from base_extractor import BaseExtractor
import parsedatetime as pdt

class DateAndTimeExtractor(BaseExtractor):
    @staticmethod
    def extract(message, context):
      body = message.get('payload').get('body')
      cal = pdt.Calendar()
      date_header = message.get_header('Date')
      if not date_header:
        DateAndTimeExtractor.throw()
      start_date = cal.parse()[0]
      dates = cal.nlp(body, sourceTime=start_date)
      if dates:
        return {'datetime': dates[0]}, {}
      else:
        DateAndTimeExtractor.throw()

