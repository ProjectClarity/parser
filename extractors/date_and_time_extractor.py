import parsedatetime as pdt

def DateAndTimeExtractor(BaseExtractor):
    @staticmethod
    def extract(message):
      body = message.get('body')
      cal = pdt.Calendar()
      start_date = cal.parse(body.get_header('Date'))

