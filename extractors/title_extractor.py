import re
from base_extractor import BaseExtractor

class TitleExtractor(BaseExtractor):
    @staticmethod
    def extract(message, context):
       subject = message.get_header('Subject')
       if any([x in subject.lower() for x in ['digest', 'activate']]):
        TitleExtractor.throw()
       unbracketed = re.sub(r'\[.*?\]', r'', subject)
       return {'title': unbracketed}, {}
