import json, urllib2, os
from mongo import get_raw_email, store_processed_data, DuplicateException
from extractors import extractors, NotAnEventException
from message import Message

def get_events_from_email(raw_email):
    message = Message(raw_email)
    # Segmenting goes here
    results = {}
    context = {}
    results['email_id'] = raw_email['id']
    results['user_id'] = raw_email['userid']
    for extractor in extractors:
        new_results, new_context = extractor.extract(message, context)
        results.update(new_results)
        context.update(new_context)
    return [results]

def post_events(event_ids):
    payload = {'event_ids': event_ids}
    req = urllib2.Request('{}/events/create'.format(os.getenv('API_URL')))
    req.add_header('Content-Type', 'application/json')
    urllib2.urlopen(req, json.dumps(payload))


def process_notification(notification):
    object_id = notification['object_id']
    try:
        with get_raw_email(object_id) as raw_email:
            events = get_events_from_email(raw_email)
            event_ids = [str(store_processed_data(event)) for event in events]
            try:
                post_events(event_ids)
            except (urllib2.HTTPError, urllib2.URLError) as e:
                print 'Error POSTing: {}'.format(e)
            print 'Processed {} events'.format(len(events))
    except (DuplicateException, NotAnEventException):
        pass
    except:
        raise
