import json

def lambda_handler(event, context):
    for record in event['Records']:
        sns_message = json.loads(record['body'])
        order_data = json.loads(sns_message['Message'])
        order_id = order_data['order_id']
        item_name = order_data['item_name']

        # In a real system this would call SES or a push-notification service.
        # Logging simulates the notification for this project's scope.
        print(f"Notification: Order {order_id} for '{item_name}' has been placed successfully.")

    return {'statusCode': 200}