from flask import Blueprint,request,jsonify
import boto3
from boto3.dynamodb.conditions import Key,Attr

general_query=Blueprint('general_query',__name__,static_folder=None,template_folder=None)
dynamodb=boto3.resource('dynamodb',region_name='us-east-2')
table=dynamodb.Table('CommentService')
client=boto3.client('dynamodb','us-east-2')

@general_query.route('/comment')
def comment():
    email=request.args.get('email')
    if email:
        comments=table.query(
            IndexName='emailIndex',
            KeyConditionExpression='email=:eml',
            ExpressionAttributeValues={
                ':eml':email
            }
        )['Items']
    print(comments)

    return jsonify({'comments':comments}),200




@general_query.route('/user')
def user():

    pass

@general_query.route('/game')
def game():
    pass


@general_query.route('/post')
def post():
    pass




