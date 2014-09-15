from base_extractor import BaseExtractor
import email.utils

class SourceExtractor(BaseExtractor):
    @staticmethod
    def extract(message, context):
      _from = message.get_header('From').lower()
      from_name, from_email = email.utils.parseaddr(_from)
      if from_email in ['info@twitter.com', 'calendar-notification@google.com']:
        SourceExtractor.throw()
      if any(x in from_email.split('@')[0].replace('-','') for x in ['noreply']):
        SourceExtractor.throw()
      if from_email.split('@')[-1] in ['facebookmail.com', 'mail.cnn.com']:
        SourceExtractor.throw()
      if from_name:
        return {'source': from_name, 'email': from_email}, {}
      else:
        return {}, {}

