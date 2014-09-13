from mongo import get_raw_email, store_processed_email
from extractors import extractors

def process_email(raw_email):
    results = {}
    results['email_id'] = raw_email['id']
    for extractor in extractors:
        results.update(extractor.extract(raw_email))
    
def process_notification(notification):
    object_id = notification['object_id']
    with get_raw_email(object_id) as raw_email:
        if raw_email is None:
            return
        processed_email = process_email(raw_email)
        store_processed_email(processed_email)
    return processed_email
