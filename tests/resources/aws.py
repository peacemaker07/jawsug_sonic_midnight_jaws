import boto3


def setup_s3(bucket_name='mock-aws-with-moto-test'):

    # bucket
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucket_name)
    bucket.create()


def setup_dynamodb_s3_info():
    dynamodb = boto3.resource(service_name='dynamodb', region_name='ap-northeast-1')

    dynamodb.create_table(
        TableName='s3-info-dev',
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


def setup_sqs(name='mock-sample-queue-dev'):

    sqs = boto3.resource('sqs', region_name='ap-northeast-1')
    return sqs.create_queue(
        QueueName=name,
        Attributes={
            'VisibilityTimeout': '660'
        },
    )


def get_sqs_messages(name='mock-sample-queue-dev'):

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
