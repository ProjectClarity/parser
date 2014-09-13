import re

from base_extractor import BaseExtractor

class TitleExtractor(BaseExtractor):
    @staticmethod
    def extract(message):
       subject = message.get_header('Subject')
       unbracketed = re.sub(r'\[.*?\]', r'', subject)
       return {'title': unbracketed}, {}
