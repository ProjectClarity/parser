from base_extractor import BaseExtractor
import parsedatetime as pdt

class DateAndTimeExtractor(BaseExtractor):
    @staticmethod
    def extract(message):
      body = message.get('payload').get('body')
      cal = pdt.Calendar()
      start_date = cal.parse(message.get_header('Date'))[0]
      dates = cal.nlp(body, sourceTime=start_date)
      if dates:
        return {'datetime': dates[0]}
      else:
        DateAndTimeExtractor.throw()

