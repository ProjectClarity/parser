import json, urllib2, os
from mongo import get_raw_email, store_processed_data, DuplicateException, NoSuchEmailException
from extractors import extractors, NotAnEventException
from refiners import refiners
from message import Message

def get_events_from_email(raw_email):
    message = Message(raw_email)
    # Segmenting goes here
    results = {} # Stored and used
    context = {} # Intermediate results
    results['email_id'] = raw_email['id']
    results['user_id'] = raw_email['userid']
    results['original_body'] = raw_email.get('payload').get('body')
    for extractor in extractors: # Get information out of the message
        new_results, new_context = extractor.extract(message, context)
        results.update(new_results)
        context.update(new_context)
    for refiner in refiners: # Post-process the results
        new_results, new_context = refiner.refine(results, context)
        results.update(new_results)
        context.update(new_context)
    # TODO: Add filters, one being duplicate events
    return [results]

def post_events(event_ids):
    payload = {'event_ids': event_ids}
    req = urllib2.Request('{}/events/create'.format(os.getenv('API_URL')))
    req.add_header('Content-Type', 'application/json')
    return urllib2.urlopen(req, json.dumps(payload))

def process_notification(notification):
    object_id = notification['object_id']
    try:
        with get_raw_email(object_id) as raw_email:
            events = get_events_from_email(raw_email)
            event_ids = [str(store_processed_data(event)) for event in events]
            try:
                resp = json.loads(post_events(event_ids).read())
                print 'Created Events: ' + ', '.join(resp['ids'])
            except (urllib2.HTTPError, urllib2.URLError) as e:
                print 'Error POSTing: {}'.format(e)
            except e:
                print 'Unknown Exception: {}'.format(e)
    except (DuplicateException, NotAnEventException, NoSuchEmailException):
        pass
    except:
        raise
