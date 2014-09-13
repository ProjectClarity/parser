from sqs_conn import *

def send_to_queue(dict):
    notification = JSONMessage()
    notification.update(dict)
    importer_queue.write(notification)

def get_notifications(num):
    return importer_queue.get_notifications(num_notifications=n, wait_time_seconds=20)

def delete_notification(notification):
    importer_queue.delete_notification(notification)

def delete_notifications(list_of_notifications):
    importer_queue.delete_notification_batch(list_of_notifications)

def process_notifications(list_of_notifications, func):
    for notification in list_of_notifications:
      func(notification)
      delete_notification(notification)
