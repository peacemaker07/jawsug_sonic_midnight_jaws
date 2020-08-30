import json
import boto3

s3 = boto3.resource('s3', region_name='ap-northeast-1')
ssm = boto3.client('ssm', region_name='ap-northeast-1')
sqs = boto3.resource('sqs', region_name='ap-northeast-1')


def s3_trigger_and_move(event, context):
    """
    event内容:
    {
        "Records": [{
            "eventVersion": "2.1",
            "eventSource": "aws:s3",
            "awsRegion": "ap-northeast-1",
            "eventTime": "2020-08-29T10:38:27.247Z",
            "eventName": "ObjectCreated:Put",
            "userIdentity": {
                "principalId": "AWS:XXXX"
            },
            "requestParameters": {
                "sourceIPAddress": "XXX.XXX.XXX.XXX"
            },
            "responseElements": {
                "x-amz-request-id": "F14105EF5F76A5A7",
                "x-amz-id-2": "KohLZ6InlVR8BvO6G8/s80pZU1MzpHp/wnXK1CmEv6DioxJgY8rEGaMZAieWletHP1YVbhOo6NE1Jha4Rc6r8H+l/KBTf4y3"
            },
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "jawsug-sonic-midnight-jaws-dev-s3_trigger_and_move-e9570fa7c86cce4df943f4c116563d60",
                "bucket": {
                    "name": "mock-aws-with-moto-dev",
                    "ownerIdentity": {
                        "principalId": "XXXX"
                    },
                    "arn": "arn:aws:s3:::mock-aws-with-moto-dev"
                },
                "object": {
                    "key": "uploads/0089BAC2-DF5C-43DE-9AAA-5468CCA70AF6.jpg",
                    "size": 39008,
                    "eTag": "8e86e2bee80365e689e2094c515230a1",
                    "sequencer": "005F4A3025CD5381B7"
                }
            }
        }]
    }
    """

    print(event)
    #
    # bucket名、オブジェクトキーを取得
    #
    records = event['Records']
    bucket_name = records[0]['s3']['bucket']['name']
    obj_key = records[0]['s3']['object']['key']

    #
    # 画像を処理済みに移動
    #
    bucket = s3.Bucket(bucket_name)
    # 移動先へコピー
    to_obj_key = f'finish/{obj_key.split("/")[-1]}'
    to_obj = bucket.Object(to_obj_key)
    copy_source = {
        'Bucket': bucket_name,
        'Key': obj_key
    }
    to_obj.copy(copy_source)
    # 移動元を削除する
    obj = bucket.Object(obj_key)
    obj.delete()

    #
    # SQSのQueueへ送信
    #
    # ※ Queue名の取得はLambdaの環境変数などへ設定すれば良い感じですが、、、
    #   今回はパラメータストアの例も記載したいため、パラメータストアに
    #   Queue名を保持するようにしました
    response = ssm.get_parameter(
        Name='mock_sqs_queue_name',
        WithDecryption=True
    )
    queue_name = response['Parameter']['Value']
    queue = sqs.get_queue_by_name(QueueName=queue_name)
    message = {
        'MessageBody': json.dumps({
            'bucket_name': bucket_name,
            'obj_key': obj_key,
        }),
    }
    response = queue.send_message(**message)
    print(response)
