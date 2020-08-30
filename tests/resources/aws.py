import os
import boto3

from tests.helper import get_abspath


def setup_s3(bucket_name, obj_key=None):

    # bucket
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.create()

    # put
    if obj_key:
        # put image
        bucket = s3.Bucket(bucket_name)
        data = open(os.path.join(get_abspath(), 'GL_LOGO.jpg'), mode='rb')
        result = bucket.put_object(Key=obj_key, Body=data)


def setup_dynamodb_s3_info(table_name):
    dynamodb = boto3.resource(service_name='dynamodb', region_name='ap-northeast-1')

    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'bucket_name',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'timestamp',
                'KeyType': 'RANGE'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'bucket_name',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'N'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 3,
            'WriteCapacityUnits': 3,
        }
    )


def setup_sqs(name):

    sqs = boto3.resource('sqs', region_name='ap-northeast-1')
    return sqs.create_queue(
        QueueName=name,
        Attributes={
            'VisibilityTimeout': '660'
        },
    )


def get_sqs_messages(name):

    sqs = boto3.resource('sqs', region_name='ap-northeast-1')
    queue = sqs.get_queue_by_name(QueueName=name)
    return queue.receive_messages()


def setup_parameter_store(name, value, value_type='String'):

    ssm = boto3.client('ssm', region_name='ap-northeast-1')
    ssm.put_parameter(
        Name=name,
        Value=value,
        Type=value_type,
        Overwrite=True,
    )
