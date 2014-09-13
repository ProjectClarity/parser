from mongo import get_raw_email, store_processed_data, DuplicateException
from extractors import extractors

def process_email(raw_email):
    results = {}
    results['email_id'] = raw_email['id']
    results['user_id'] = raw_email['userid']
    for extractor in extractors:
        results.update(extractor.extract(raw_email))
    return results

def process_notification(notification):
    object_id = notification['object_id']
    try:
        with get_raw_email(object_id) as raw_email:
            processed_email = process_email(raw_email)
            store_processed_data(processed_email)
        return processed_email
    except DuplicateException:
        pass
    except:
        raise
