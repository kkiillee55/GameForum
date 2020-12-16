import boto3

dynamodb=boto3.resource('dynamodb',region_name='us-east-2')
table=dynamodb.create_table(
    TableName='CommentService',
    KeySchema=[
        {
            'AttributeName':'comment_id',
            'KeyType':'HASH'
        },
        {
            'AttributeName':'email',
            'KeyType':'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName':'comment_id',
            'AttributeType':'S'
        },
        {
            'AttributeName':'email',
            'AttributeType':'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)
table.meta.client.get_waiter('table_exists').wait(TableName='CommentService')
