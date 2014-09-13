import re, urllib2
from base_extractor import BaseExtractor

URL_REGEX = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')

class HeadRequest(urllib2.Request):
  def get_method(self):
      return "HEAD"

class HTTPRedirectHandler(urllib2.HTTPRedirectHandler):
  def redirect_request(self, req, fp, code, msg, headers, newurl):
    newreq = urllib2.HTTPRedirectHandler.redirect_request(self,
        req, fp, code, msg, headers, newurl)
    if newreq is not None:
        self.redirections.append(newreq.get_full_url())
    return newreq

def get_last_redirect(link):
  try:
    redirect_handler = HTTPRedirectHandler()
    redirect_handler.max_redirections = 100
    redirect_handler.redirections = [link]
    opener = urllib2.build_opener(redirect_handler)
    request = HeadRequest(link)
    opener.open(request)
    return redirect_handler.redirections[-1]
  except:
    return None

class LinkExtractor(BaseExtractor):
  @staticmethod
  def extract(message, context):
   body = message.get('payload').get('body')
   matches = URL_REGEX.findall(body)
   links = filter(lambda x: bool(x), [get_last_redirect(match[0]) for match in matches])
   return {}, {'links': links}
