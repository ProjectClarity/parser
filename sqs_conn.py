import boto, os
from boto.sqs.jsonmessage import JSONMessage

sqs_conn = boto.sqs.connect_to_region("us-east-1")
importer_queue = sqs_conn.get_queue(os.environ.get('SQS_QUEUE'))
importer_queue.set_message_class(JSONMessage)
