import json
import pytest
import boto3
from botocore.exceptions import ClientError
from moto import mock_s3, mock_ssm, mock_sqs

from tests.resources.aws import (
    setup_s3,
    setup_sqs,
    setup_parameter_store,
    get_sqs_messages,
)
from handler import s3_trigger_and_move

s3 = boto3.client('s3', region_name='ap-northeast-1')


@pytest.fixture()
def s3_trigger_event():

    return {
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
                    "name": "mock-aws-with-moto-test",
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


@mock_s3
@mock_sqs
@mock_ssm
def test_s3trigger_and_move_success(s3_trigger_event):
    """
    画像の移動が正常に行われ、SQSへS3の情報を送信すること
    """
    # setup
    bucket_name = s3_trigger_event['Records'][0]['s3']['bucket']['name']
    obj_key = s3_trigger_event['Records'][0]['s3']['object']['key']
    setup_s3(bucket_name, obj_key=obj_key)
    queue_name = 'mock-sample-queue-test'
    setup_sqs(queue_name)
    setup_parameter_store('mock_sqs_queue_name', queue_name)

    # 実行
    s3_trigger_and_move(s3_trigger_event, '')

    # アップロード先には画像がないこと
    try:
        _ = s3.get_object(Bucket=bucket_name, Key=obj_key)
    except ClientError as e:
        # 移動したため、移動元は画像なし
        assert e.response['Error']['Code'] == 'NoSuchKey'

    # 移動先に画像があること
    image_filename = obj_key.split('/')[-1]
    to_obj_key = f'finish/{image_filename}'
    response = s3.get_object(Bucket=bucket_name, Key=to_obj_key)
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200

    # Queueのメッセージが正常にセットされていること
    msg_list = get_sqs_messages(queue_name)
    assert len(msg_list) == 1
    message_body = json.loads(msg_list[0].body)
    assert len(message_body) == 2
    assert message_body['bucket_name'] == bucket_name
    assert message_body['obj_key'] == obj_key
