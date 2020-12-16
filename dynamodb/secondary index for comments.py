import boto3
client=boto3.client('dynamodb',region_name='us-east-2')
client.update_table(
    TableName='CommentService',
    AttributeDefinitions=[
        {
            'AttributeName':'email',
            'AttributeType':'S'
        },
    ],
    GlobalSecondaryIndexUpdates=[
        {
            'Create':{
                'IndexName':'emailIndex',
                'KeySchema':[
                    {
                        'AttributeName':'email',
                        'KeyType':'HASH'
                    }
                ],
                'Projection':{
                    'ProjectionType':'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
                }
            }
        }
    ]
)


# client.update_table(
#     TableName='CommentService',
#     AttributeDefinitions=[
#         {
#             'AttributeName':'comment_id',
#             'AttributeType':'S'
#         },
#     ],
#     GlobalSecondaryIndexUpdates=[
#         {
#             'Create':{
#                 'IndexName':'commentIndex',
#                 'KeySchema':[
#                     {
#                         'AttributeName':'comment_id',
#                         'KeyType':'HASH'
#                     }
#                 ],
#                 'Projection':{
#                     'ProjectionType':'ALL'
#                 },
#                 'ProvisionedThroughput': {
#                     'ReadCapacityUnits': 1,
#                     'WriteCapacityUnits': 1
#                 }
#             }
#         }
#     ]
# )
#
#
# client.update_table(
#     TableName='CommentService',
#     AttributeDefinitions=[
#         {
#             'AttributeName':'post_id',
#             'AttributeType':'S'
#         },
#     ],
#     GlobalSecondaryIndexUpdates=[
#         {
#             'Create':{
#                 'IndexName':'postIndex',
#                 'KeySchema':[
#                     {
#                         'AttributeName':'post_id',
#                         'KeyType':'HASH'
#                     }
#                 ],
#                 'Projection':{
#                     'ProjectionType':'ALL'
#                 },
#                 'ProvisionedThroughput': {
#                     'ReadCapacityUnits': 1,
#                     'WriteCapacityUnits': 1
#                 }
#             }
#         }
#     ]
# )