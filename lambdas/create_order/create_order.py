import json
import uuid
import boto3
from typing import Any
from datetime import datetime, timezone

dynamodb: Any = boto3.resource('dynamodb')
table = dynamodb.Table('Orders')

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

        return {
            'statusCode': 201,
            'body': json.dumps({'order_id': order_id, 'status': 'PENDING'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }