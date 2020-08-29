import json
import time
from datetime import datetime
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')


def sqs_trigger_and_save(event, context):
    """
    event内容:
    {
        "Records": [
            {
                "messageId": "cd5844f0-ab00-4fb2-97ad-e2bdeced6b64",
                "receiptHandle": "AQEB2JbFPLIiPMt4ROd7YbpcS4chPywRAY6GtWk0vMXFKvzy/thtb4sYQ2xKWUsFcsaTylTJNb9ZTfoeSjgbUaettggmSt3VxBxMdgsaNT9WoKT/bBUESWPkUMlHAtXsFGrjMvt93MqQvaGtWo0fVy17Q5ry3wGaYDmTYnl8Y5H7C4XetSg0Gtj9HA9KMt/qb1p2rXCbv+a4F6CwvGQgBXE027/EVbcsCiADIMDMLoGUNZYg782t6l1FPHp7rkyMgdF/ZMOqohQH9zfkyVivAGRpGJepLSQ6zyJD+Se81Ro+cEqMXcxAM6pBrI2S0TatD5jr3N6Bd0A70/yx1MUVY5En2WKzyFyc647GDpSWDUo9EYIrUQCQ6RtR/rzjaQyr23KjP//l53eNsf80ZGuKkMcKut149oI1PvqVnoh+502AM2g=",
                "body": "{\"bucket_name\": \"mock-aws-with-moto-dev\", \"obj_key\": \"uploads/350C448F-0B64-4FAC-AE46-CAA2A9A21048.jpg\"}",
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1598710272184",
                    "SenderId": "AROAQDSXCILMCPMMQSSN5:jawsug-sonic-midnight-jaws-dev-s3_trigger_and_move",
                    "ApproximateFirstReceiveTimestamp": "1598710272191"
                },
                "messageAttributes": {},
                "md5OfBody": "e456e4dcae58d364774a009736b582d0",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:ap-northeast-1:007698793176:mock-sample-queue-dev",
                "awsRegion": "ap-northeast-1"
            }
        ]
    }
    """

    print(event)
    # メッセージの内容を取得
    message_body_str = event['Records'][0]['body']
    message_body = json.loads(message_body_str)
    bucket_name = message_body['bucket_name']
    obj_key = message_body['obj_key']

    # テーブルへput
    table = dynamodb.Table('s3-info-dev')
    response = table.put_item(Item={
        'bucket_name': bucket_name,
        'timestamp': int(time.mktime(datetime.now().timetuple())),
        'obj_key': obj_key,
    })
    print(response)
