import boto3
from boto3.dynamodb.conditions import Key,Attr
import time
dynamodb=boto3.resource('dynamodb',region_name='us-east-2')
table=dynamodb.Table('CommentService')

# post_id=7
#
#
#
# def t1(post_id):
#     comments = table.query(
#         IndexName='postIndex',
#         KeyConditionExpression='post_id=:pid',
#         ExpressionAttributeValues={
#             ':pid': str(post_id)
#         }
#     )
#
# def t2(post_id):
#     comments=table.scan(
#         FilterExpression=Attr("post_id").eq(str(post_id))
#     )
#
# for i in [3,4,6,7,8,9,10,11]:
#     t2(i)
#     t1(i)
# t1_time=0
# t2_time=0
# for x in range(5):
#     print(x)
#     start=time.time()
#     for i in [3,4,6,7,8,9,10,11]:
#         t1(i)
#     end=time.time()
#     t1_time+=(end-start)
#
#
#     start=time.time()
#     for i in [3,4,6,7,8,9,10,11]:
#         t2(i)
#     end=time.time()
#     t2_time+=(end-start)
# print(t1_time)
# print(t2_time)
comment_id='0846c760-dc13-4cff-85d8-d979cd04e8c6'
email='xl2875@columbiia.edu'
table.delete_item(Key={
    'comment_id': comment_id
})




