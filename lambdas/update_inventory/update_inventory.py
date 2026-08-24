import json
import boto3
from typing import Any

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Orders') # type: ignore

def lambda_handler(event, context):
    for record in event['Records']:
        # SNS-wrapped message inside SQS body
        sns_message = json.loads(record['body'])
        order_data = json.loads(sns_message['Message'])
        order_id = order_data['order_id']

        # Idempotency check: only update if not already processed.
        # ConditionExpression makes this atomic — if two deliveries of the
        # same message arrive (at-least-once delivery), only the first
        # succeeds; the second raises ConditionalCheckFailedException
        # and is safely ignored.
        assert dynamodb.meta is not None
        try:
            table.update_item(
                Key={'order_id': order_id},
                UpdateExpression='SET inventory_updated = :true, #s = :status',
                ConditionExpression='inventory_updated = :false',
                ExpressionAttributeNames={'#s': 'status'},
                ExpressionAttributeValues={
                    ':true': True,
                    ':false': False,
                    ':status': 'INVENTORY_UPDATED'
                }
            )
            print(f"Inventory updated for order {order_id}")
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            print(f"Order {order_id} already processed — skipping duplicate delivery")

    return {'statusCode': 200}