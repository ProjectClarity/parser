from base_extractor import BaseExtractor
import parsedatetime as pdt
from email.utils import parsedate
import re, os, requests, dateutil.parser, time, datetime

def validate_date(date, body, context):
  parsed_datetime, flags, start_pos, end_pos, date_text = date
  if any([date_text in x for x in context['original_links']]):
    return False
  if re.search(r'\s[A-Za-z]$', date_text):
    return False
  if re.search(r'\s\d{3,}$', date_text):
    return False
  if re.search(r'\d{3,}\s?(am|pm)$', date_text, re.IGNORECASE):
    return False
  matches = re.search(r'(\d{1,2})[\.:]\d{1,2}|(\d{1,2})\s?(am|pm)', date_text, re.IGNORECASE)
  if matches:
    if (matches.group(1) and int(matches.group(1)) > 12) or (matches.group(2) and int(matches.group(2)) > 12):
      return False
  if "\n" in date_text:
    return False
  if len(date_text) < 5 and not any([x in date_text.lower() for x in ['-', '/', 'am', 'pm']]):
    return False
  if date_text.isdigit():
    return False
  if date_text.startswith('--'):
    return False
  if not any([x in date_text for x in [' ', '-', '/']]):
    return False
  if any([x in body[end_pos+1:end_pos+5].lower() for x in ['am', 'pm']]):
    return False

  return True

def parse_date_manually(body, timeref, context):
  cal = pdt.Calendar()
  try:
    dates = cal.nlp(body, sourceTime=timeref)
  except:
    DateAndTimeExtractor.throw()
  if dates:
    dates = list(filter(lambda x: validate_date(x, body, context), dates))
    # dates.sort(key=lambda x: len(x[-1]))
    for date in dates:
      if date[-1][0].isdigit():
        return {'datetime': date}, {}
    for date in dates:
      if date[-1][0].isupper():
        return {'datetime': date}, {}
    for date in dates:
      if date[-1][0] not in ['tonight', 'today', 'tomorrow']:
        return {'datetime': date}, {}
    if dates:
      return {'datetime': dates[0]}, {}
    DateAndTimeExtractor.throw()
  else:
    DateAndTimeExtractor.throw()

def parse_date(string):
  return dateutil.parser.parse(string)

def score_normalized_form(normalized_form):
  return len([x for x in normalized_form.split('|') if x])

def score_normalized_form_weighted(normalized_form):
  components = normalized_form.split('|')
  score = 0
  for i, comp in enumerate(components):
    if comp:
      score += i + 1
  return score

def get_date_from_forms(forms):
  precisions = {}
  for form in forms:
    precision = form.get('precision')
    if not precision:
      continue
    try:
      precisions[precision].append(form)
    except:
      precisions[precision] = [form]
  for x in ['minutesAMPM', 'hourAMPM']:
    if precisions.get(x):
      for form in precisions.get(x):
        if score_normalized_form(form['normalized_form']) > 2:
          return form.get('actual_time') or parse_date(form['form'])
  date_components = []
  for x in [('weekday',[], ''), ('day', [6], ''), ('hourAMPM', [7], ':00'), ('minutesAMPM', [7, 8], '')]:
    if precisions.get(x[0]):
      best = sorted(precisions.get(x[0]), key=lambda y: score_normalized_form_weighted(y['normalized_form']))[0]
      comp = best.get("actual_time")
      if not comp:
        if x[1]:
          components = best['normalized_form'].split('|')
          comp = ' '.join(components[i] for i in x[1]) + x[2]
        else:
          comp = best['form']
      date_components.append(comp)
  while True:
    try:
      return parse_date(' '.join(date_components))
    except:
      date_components = date_components[:-1]
      if not date_components:
        DateAndTimeExtractor.throw()

class DateAndTimeAPIAccount():
  def __init__(self, body, timeref, mime_type):
    timeref = datetime.datetime.fromtimestamp(time.mktime(timeref))
    offset_str = timeref.strftime('%z')
    if offset_str:
      offset_str = offset_str[:-2] + ':' + offset_str[-2:]
    else:
      offset_str = '+00:00'
    self.timeref = timeref.strftime('%Y-%m-%d %H:%M:%S GMT') + offset_str
    self.body = body
    self.mime_type = mime_type
  def make_api_call(self):
    params = {
      'key': os.getenv('TOPIC_EXTRACTION_API_KEY'),
      'of': 'json',
      'lang': 'en',
      'txt': self.body,
      'txtf': 'plain' if self.mime_type is 'text/plain' else 'markup',
      'tt': 'tmupr',
      'timeref': self.timeref,
      'dic': 'chetsdpCSA'
    }
    return requests.post(os.getenv('TOPIC_EXTRACTION_API'), params=params).json()

class DateAndTimeExtractor(BaseExtractor):
    @staticmethod
    def extract(message, context):
      body = message.get('payload').get('body')
      date_header = message.get_header('Date')
      mime_type = message.get('payload').get('mimeType') or 'text/plain'
      if not date_header:
        DateAndTimeExtractor.throw()
      timeref = parsedate(date_header)
      api = DateAndTimeAPIAccount(body, timeref, mime_type)
      response = api.make_api_call()
      time_exps = response['time_expression_list']
      try:
        return {'datetime': get_date_from_forms(time_exps)}, {}
      except:
        DateAndTimeExtractor.throw()



