import time

from sqs_helpers import get_notifications, process_notifications
from pipeline import process_notification

MAX_NOTIFICATION_BATCH_SIZE = 10

if __name__ == '__main__':
    while True:
        newest_notifications = get_notifications(MAX_NOTIFICATION_BATCH_SIZE)
        process_notifications(newest_notifications, process_notification)
        time.sleep(20)

