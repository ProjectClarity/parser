Python project to do the heavy lifting:

-Receive SQS notifications for new raw emails
-Retrieve raw emails and metadata
-Extract relevant content
-Add relevant value
-Store parsed events
-Cleanup
-Send appropriate notifications via websockets
