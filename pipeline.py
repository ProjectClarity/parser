import json
import urllib2

from mongo import get_raw_email, store_processed_data, DuplicateException
from extractors import extractors, NotAnEventException
from message import Message

def process_email(raw_email):
    message = Message(raw_email)
    # Segmenting goes here
    results = {}
    results['email_id'] = raw_email['id']
    results['user_id'] = raw_email['userid']
    for extractor in extractors:
        results.update(extractor.extract(message))
    return results

def post_events(event_ids):
    payload = {'event_ids': event_ids}

    req = urllib2.Request('http://pennappsx-web.herokuapp.com/events/create')
    req.add_header('Content-Type', 'application/json')

    urlopen(req, json.dumps(payload))


def process_notification(notification):
    object_id = notification['object_id']
    try:
        with get_raw_email(object_id) as raw_email:
            processed_email = process_email(raw_email)
            event_ids = []
            for i in xrange(1): # Change to actually loop over all events
                event_object_id = store_processed_data(processed_email)
                event_ids.append(str(event_object_id))
            post_events(event_ids)
    except (DuplicateException, NotAnEventException):
        pass
    except:
        raise
