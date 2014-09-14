import re
import urllib2

from base_extractor import BaseExtractor

whitelist = [re.compile(regex) for regex in ['list-manage\d\.com']]

class CustomHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        newreq = urllib2.HTTPRedirectHandler.redirect_request(self,
            req, fp, code, msg, headers, newurl)
        if newreq is not None:
            self.redirections.append(newreq.get_full_url())
        return newreq

def follow(link):           
    if any(regex.search(link) for regex in whitelist):
        redirect_handler = CustomHTTPRedirectHandler()
        redirect_handler.max_redirections = 100
        redirect_handler.redirections = [link]
        opener = urllib2.build_opener(redirect_handler)
        request = urllib2.Request(link)
        request.get_method = lambda : 'HEAD'
        response = opener.open(request)
        return redirect_handler.redirections[-1]

class LinkExtractor(BaseExtractor):
    @staticmethod
    def extract(message):
       body = message # message.get('payload').get('body')
       url_pattern = re.compile(r'((\S+?\.)+(\S+))')
       matches = url_pattern.findall(body)
       if len(matches) == 0:
           return {}, {'links':[]}
       links = [match[0] for match in matches]
       links = [follow(link) for link in links]
       return {}, {'links': links}
