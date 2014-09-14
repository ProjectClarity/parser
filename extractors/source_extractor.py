from base_extractor import BaseExtractor
import email.utils

class SourceExtractor(BaseExtractor):
    @staticmethod
    def extract(message, context):
      _from = message.get_header('From')
      from_name, from_email = email.utils.parseaddr(_from)
      if from_email.split('@')[-1].lower() in ['facebookmail.com', 'twitter.com', 'meetup.com']:
        SourceExtractor.throw()
      if from_name:
        return {'source': from_name, 'email': from_email}, {}
      else:
        return {}, {}

