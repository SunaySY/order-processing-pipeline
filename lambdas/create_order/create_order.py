import json
import uuid
import boto3
from typing import Any
from datetime import datetime, timezone

dynamodb: Any = boto3.resource('dynamodb')
table = dynamodb.Table('Orders')
sns = boto3.client('sns')

TOPIC_ARN = 'arn:aws:sns:ap-south-1:565881507579:order-events'

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        item_name = body.get('item_name')
        quantity = body.get('quantity')

        if not item_name or not quantity:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'item_name and quantity are required'})
            }

        order_id = str(uuid.uuid4())

        table.put_item(
            Item={
                'order_id': order_id,
                'item_name': item_name,
                'quantity': quantity,
                'status': 'PENDING',
                'inventory_updated': False,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
        )

        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps({
                'order_id':order_id,
                'item_name':item_name,
                'quantity':quantity
            }),
            Subject='NewOrder'
        )

        return {
            'statusCode': 201,
            'body': json.dumps({'order_id': order_id, 'status': 'PENDING'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }