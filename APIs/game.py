from flask import Blueprint,jsonify,request,url_for,session
from models import Game,Post,User,Comment
from utils import token_required,get_current_user
import jwt
from modules import application,db
from uuid import uuid4
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Key,Attr

import requests
from requests_aws4auth import AWS4Auth
import os
game=Blueprint('game',__name__,static_folder=None,template_folder=None)

region='us-east-2'
dynamodb=boto3.resource('dynamodb',region_name=region)
table=dynamodb.Table('CommentService')
client=boto3.client('dynamodb',region)

service='es'
credentials=boto3.Session().get_credentials()
awsauth=AWS4Auth(credentials.access_key,credentials.secret_key,region,service,session_token=credentials.token)
es_host=os.environ.get('es_host')
index='comments'
type='_doc'
url=f'{es_host}/{index}/{type}/'
headers={"Content-Type": "application/json"}






@game.route('/')
def home():
    res={}
    res['msg']='game home page'
    res['links']=[]
    games=Game.query.all()
    for game in games:
        temp={
            'rel':game.title,
            'href':f'{url_for("game.game_posts",game_title=game.title)}'
        }
        res['links'].append(temp)
    return jsonify(res),200

@game.route('/<string:game_title>')
def game_posts(game_title):
    game=Game.query.filter_by(title=game_title).first()
    user=get_current_user()
    res={}
    res['links']=[
        # {
        #     'rel':'game home page',
        #     'href':f'{url_for("game.home")}'
        # },
        {
            'rel': 'post/new_post',
            'href': f'{url_for("game.new_post", game_title=game_title)}'
        }
        # {
        #     'rel':'unfollow this game' if (user and game in user.following_games) else 'follow this game',
        #     'href':f'{url_for("game.unfollow",game_title=game_title)}' if (user and game in user.following_games) else f'{url_for("game.follow",game_title=game_title)}'
        # },
    ]
    if user:
        if game in user.following_games:
            res['links']+=[
                {
                    'rel':'action/unfollow',
                    'href':f'{url_for("game.unfollow",game_title=game_title)}'

                }
            ]
        else:
            res['links'] += [
                {
                    'rel': 'action/follow',
                    'href': f'{url_for("game.follow", game_title=game_title)}'

                }
            ]
    # if user and game in user.following_games:
    #     res['links']+=[
    #         {
    #             'rel':'create post',
    #             'href':f'{url_for("game.new_post",game_title=game_title)}'
    #         }
    #     ]
    if not game:
        return jsonify({
            'msg': 'game not found',
            'links':[
                {
                    'rel': 'game home page',
                    'href': f'{url_for("game.home")}'
                }
            ]
        }),404
    else:
        res['title']=game.title
        res['release date']=game.release_date
        res['platform']=[platform.name for platform in game.platforms]
        res['posts']=[{
            'title':post.title,
            'abstract':post.content[:10]+"...",
            'post_id':post.id,
            'author':f'{post.author.first_name} {post.author.last_name}',
            'date_posted':post.date_posted,
            'href':f'{url_for("game.post_page",game_title=game_title,post_id=post.id)}'
        } for post in game.posts]
        return jsonify(res),200

@game.route('/<string:game_title>/<int:post_id>')
def post_page(game_title,post_id):
    post=Post.query.get(post_id)
    game=Game.query.filter_by(title=game_title).first()
    res={}
    res['links']=[
                {
                    'rel':'game home page',
                    'href':f'{url_for("game.home")}'
                },
            ]
    #print(post,game)
    if not post:
        res['msg']='post not found'
        return jsonify(res),404
    if not game:
        res['msg']='game not found'
        return jsonify(res),404
    res['title']=post.title
    res['date_posted']=post.date_posted
    res['author']=post.author.first_name+" "+post.author.last_name
    res['content']=post.content
    res['links'].append(
        {
            'rel': 'all game posts',
            'href': f'{url_for("game.game_posts", game_title=game_title)}'
        }
    )
    comments=table.query(
        IndexName='postIndex',
        KeyConditionExpression='post_id=:pid',
        ExpressionAttributeValues={
            ':pid':str(post_id)
        }
    )['Items']
    user=get_current_user()
    display_comments=[]
    for comment in comments:
        template={}
        template['comment_text']=comment['comment_text']
        template['datetime']=comment['datetime']
        template['links'] = []
        template['responses']=[{
            'datetime':response['datetime'],
            'email':response['email'],
            'comment_text':response['comment_text'],
            'links':[
                {
                    'rel':'update_response',
                    'href':f'{url_for("game.update_response",game_title=game_title,post_id=post_id,comment_parent_id=response["parent_id"],comment_id=response["comment_id"])}'
                },
                {
                    'rel': 'delete_response',
                    'href': f'{url_for("game.delete_response", game_title=game_title, post_id=post_id, comment_parent_id=response["parent_id"], comment_id=response["comment_id"])}'
                }
            ] if user==User.query.get(response['user_id']) else []
        } for response in comment['responses']]

        if user:
            template['links']+=[{
                'rel': 'create_response',
                'href': f'{url_for("game.create_response", game_title=game_title, post_id=post_id, comment_id=comment["comment_id"])}'
            }]
        if user==User.query.get(int(comment['user_id'])):
            template['links']+=[{
                    'rel':'delete_comment',
                    'href':f'{url_for("game.delete_comment",game_title=game_title,post_id=post_id,comment_id=comment["comment_id"])}'
                },
                {
                    'rel': 'update_comment',
                    'href': f'{url_for("game.update_comment", game_title=game_title, post_id=post_id, comment_id=comment["comment_id"])}'
                }
            ]
        display_comments.append(template)
    res['comments']=display_comments
    if user==post.author:
        res['links']+=[
            {
                'rel':'update_post',
                'href':f'{url_for("game.update_post",game_title=game_title,post_id=post_id)}'
            },
            {
                'rel': 'delete_post',
                'href': f'{url_for("game.delete_post", game_title=game_title, post_id=post_id)}'

            },
            {
                'rel':'create_comment',
                'href':f'{url_for("game.create_comment",game_title=game_title,post_id=post_id)}'

            }
        ]
    return jsonify(res),200


@game.route('/<string:game_title>/<int:post_id>/update',methods=['GET','PATCH'])
@token_required
def update_post(game_title,post_id):
    user=get_current_user()
    post=Post.query.get(post_id)
    res={}
    res['links']=[
        {
            'rel':'game home page',
            'href':f'{url_for("game.home")}'
        },
        {
            'rel':f'{game_title}',
            'href':f'{url_for("game.game_posts",game_title=game_title)}'
        }
    ]
    if not user:
        res['msg']='user not found'
        return jsonify(res),400
    if user!=post.author and not user.is_admin:
        res['msg']='you are not the author of this post'
        return jsonify(res),400
    if request.method=='GET':
        res['title']=post.title
        res['content']=post.content
        res['date_posted']=post.date_posted
        res['author']=f'{post.author.first_name} {post.author.last_name}'
        res['game']=game_title
        return jsonify(res),200
    elif request.method=='PATCH':
        res['optional fields']=['title','content']
        title=request.json.get('title')
        content=request.json.get('content')
        if title:
            post.title=title
        if content:
            post.content=content
        db.session.commit()
        res['msg']='post updated'
        return jsonify(res),200


@game.route('/<string:game_title>/<int:post_id>/delete',methods=['GET',"DELETE"])
@token_required
def delete_post(game_title,post_id):
    user = get_current_user()
    post = Post.query.get(post_id)
    res = {}
    res['links'] = [
        {
            'rel': 'game home page',
            'href': f'{url_for("game.home")}'
        },
        {
            'rel': f'{game_title}',
            'href': f'{url_for("game.game_posts", game_title=game_title)}'
        }
    ]
    if not user:
        res['msg']='user not found'
        return jsonify(res),400
    if user!=post.author and not user.is_admin:
        res['msg']='you are not the author of this post'
        return jsonify(res),400
    if request.method=='GET':
        res['title']=post.title
        res['content']=post.content
        res['date_posted']=post.date_posted
        res['author']=f'{post.author.first_name} {post.author.last_name}'
        res['game']=game_title
        return jsonify(res),200
    elif request.method == 'DELETE':
        db.session.delete(post)
        db.session.commit()

        '''
        rememeber to delete all comments in dynamodb
        '''
        comments = table.query(
            IndexName='postIndex',
            KeyConditionExpression='post_id=:pid',
            ExpressionAttributeValues={
                ':pid': str(post_id)
            }
        )['Items']
        with table.batch_writer() as batch:
            for comment in comments:
                batch.delete_item(Key={
                    'comment_id':comment['comment_id'],
                    'email':comment['email']
                })
                requests.delete(url+comment['comment_id'],auth=awsauth,headers=headers)
        res['msg']='post deleted'
        return jsonify(res),200



@game.route('/<string:game_title>/new_post',methods=['GET','POST'])
@token_required
def new_post(game_title):
    token_type,token=request.headers.get('Authorization').split(' ')
    data=jwt.decode(token,application.config['SECRET_KEY'])
    user=User.query.get(data['user_id'])
    game=Game.query.filter_by(title=game_title).first()
    res={}
    # print(game,user.following_games)
    # print(game in user.following_games)
    res['links']=[
        {
            'rel':'game home page',
            'href':f'{url_for("game.home")}'
        }
    ]
    res['fields required']=['title','content']
    if not game:
        res['msg']='game not found'
        return jsonify(res),404
    if game not in user.following_games:
        res['links'].append(
            {
                'rel':f'follow {game_title}',
                'href':f'{url_for("game.follow",game_title=game_title)}'
            }
        )
        res['msg'] = 'You need to follow this game before posting'
        return jsonify(res), 400
    if request.method=='GET':
        return jsonify(res),200
    #print('game new post')
    if request.method=='POST':

        title=request.json.get('title')
        content=request.json.get('content')

        if not title:
            res['msg']='Missing title'
            return jsonify(res),400
        if not content:
            res['msg']='Missing content'
            return jsonify(res),400
        #print('berore new post')
        new_post=Post(title=title,content=content,game=game,author=user)

        db.session.add(new_post)
        db.session.commit()

        res['msg']=f'{new_post.title} is posted'
        res['post_id']=new_post.id
        res['links'].append(
            {
                'rel':f'{new_post.title}',
                'href':f'{url_for("game.post_page",game_title=game_title,post_id=new_post.id)}'
            }
        )
        #print('in post')
        return jsonify(res),200



def add_comment(user,game_title,post_id,comment_uuid,comment_text):
    res = {}
    res['comment_id'] = comment_uuid
    res['parent_id'] = comment_uuid
    res['comment_text'] = comment_text
    res['email'] = user.email
    res['datetime'] = str(datetime.utcnow())
    res['version_id'] = str(uuid4())
    res['post_id']=str(post_id)
    res['user_id']=str(user.id)
    res['game_title']=game_title

    requests.put(url+res['comment_id'],auth=awsauth,json=res,headers=headers)

    res['responses'] = []
    table.put_item(Item=res)
    post = Post.query.get(post_id)

    comment = Comment(author=user, post=post, comment_uuid=res['comment_id'], comment_parent_uuid=res['parent_id'])
    db.session.add(comment)
    db.session.commit()

@game.route('/<string:game_title>/<int:post_id>/create_comment',methods=['POST'])
@token_required
def create_comment(game_title,post_id):
    '''
    create comment and store it in dynamodb, similar to comment service
    both comment and response have parent_id,
    parent of comment is itself
    parent of response is comment

    comment_id:uuid,
    parent_id: same as comment id,
    post_id: post_id,
    game_title:game_title,
    comment_text: string,
    email: current user email,
    datetime: str(datetime.utcnow()),
    tags: "maybe we dont need tags here",
    version_id: uuid,
    responses:[
        {
            response_id: uuid,
            parent_id: uuid of parent,
            post_id: post_id,
            game_title:game_title,
            comment_text: string,
            email: current user email,
            datetime: str(datetime.utcnow())
            version_id: uuid
        },
        {...},
        {...}
    ]

    '''
    user=get_current_user()
    #user=User.query.get(1)
    if not request.json.get('comment_text'):
        return jsonify({'msg':'missing comment_text'}),400
    uid=str(uuid4())
    add_comment(user,game_title,post_id,uid,request.json.get('comment_text'))
    return jsonify({
        'msg': 'success',
        'links':[
            {
                'rel':'return to original post',
                'href':f'{url_for("game.post_page",game_title=game_title,post_id=post_id)}'
            }
        ]
    }),200

@game.route('/<string:game_title>/<int:post_id>/<string:comment_id>/delete_comment',methods=['DELETE'])
@token_required
def delete_comment(game_title,post_id,comment_id):
    '''
    similar to delete post
    '''
    user=get_current_user()
    #user=User.query.get(1)
    comment=Comment.query.filter_by(comment_uuid=comment_id).filter_by(comment_parent_uuid=comment_id).first()
    if comment.author!=user:
        return jsonify({'msg':'you are not the author of this comment'}),400
    for row in Comment.query.filter_by(comment_parent_uuid=comment_id):
        db.session.delete(row)
    db.session.commit()
    table.delete_item(
        Key={
            'comment_id':comment_id,
            'email':user.email
        }
    )
    requests.delete(url+comment_id,auth=awsauth,headers=headers)

    return jsonify({
        'msg': 'comment deleted',
        'links':[
            {
                'rel':'original post',
                'href':f'{url_for("game.post_page",game_title=game_title,post_id=post_id)}'
            }
        ]
    }),200

@game.route('/<string:game_title>/<int:post_id>/<string:comment_id>/update_comment',methods=['GET','PATCH'])
@token_required
def update_comment(game_title,post_id,comment_id):
    '''
    similar to update post
    '''
    user=get_current_user()
    comment=Comment.query.filter_by(comment_uuid=comment_id).filter_by(comment_parent_uuid=comment_id).first()
    res={}
    res['inks']=[
        {
            'rel': 'original post',
            'href': f'{url_for("game.post_page", game_title=game_title, post_id=post_id)}'
        }
    ]
    if comment.author!=user:
        res['msg']='you are not the author of this comment'
        return jsonify(res),400

    if request.method=='GET':
        try:
            comment=table.get_item(
                Key={
                    'comment_id':comment_id,
                    'email':user.email
                }
            )['Item']
            res['version_id']=comment['version_id']
            return jsonify(res),200
        except:
            res['msg']='somethign wrong eith dynamodb'
            return jsonify(res), 400

    if not request.json.get('comment_text'):
        res['msg']='missing comment_text'
        return jsonify(res),400
    if not request.json.get('version_id'):
        res['msg']='missing version_id'
        return jsonify(res),400
    try:
        table.update_item(
            Key={
                'comment_id':comment_id,
                'email':user.email
            },
            UpdateExpression='SET comment_text=:val, version_id=:vid',
            ConditionExpression='version_id=:version_id',
            ExpressionAttributeValues={
                ':val':request.json.get('comment_text'),
                ':version_id':request.json.get('version_id'),
                ':vid':str(uuid4())
            }
        )

        comment = table.get_item(
            Key={
                'comment_id': comment_id,
                'email': user.email
            }
        )['Item']
        comment.pop('responses')

        requests.post(url+comment_id,auth=awsauth,json=comment,headers=headers)
        res['msg']='comment updated'
        return jsonify(res),200
    except:
        res['msg']='version_id dose not match'
        return jsonify(res),400

def add_response(user,game_title,post_id,comment_parent_uuid,comment_text):

    res = {}
    res['comment_id'] = str(uuid4())
    res['parent_id'] = comment_parent_uuid
    res['comment_text'] = comment_text
    res['email'] = user.email
    res['datetime'] = str(datetime.utcnow())
    res['version_id'] = str(uuid4())
    res['post_id']=str(post_id)
    res['user_id']=str(user.id)
    res['game_title']=game_title
    post = Post.query.get(post_id)
    table.update_item(
        Key={
            'comment_id':comment_parent_uuid,
            'email':post.author.email
        },
        UpdateExpression='SET responses = list_append(responses,:val)',
        ExpressionAttributeValues={
            ':val':[res]
        }
    )
    #print('in add response')

    comment = Comment(author=user, post=post, comment_uuid=res['comment_id'], comment_parent_uuid=res['parent_id'])
    db.session.add(comment)
    db.session.commit()

@game.route('/<string:game_title>/<int:post_id>/<string:comment_id>/create_response',methods=['POST'])
@token_required
def create_response(game_title,post_id,comment_id):
    '''
    create response of a comment

    response_id: uuid,
    parent_id: uuid of parents
    comment_text: string,
    email: current user email,
    datetime: str(datetime.utcnow())
    version_id: uuid
    '''


    user=get_current_user()
    #user=User.query.get(1)
    #print(user)

    if not request.json.get('comment_text'):
        return jsonify({'msg':'missing comment_text'}),400
    add_response(user,game_title,post_id,comment_id,request.json.get('comment_text'))
    return jsonify({
        'msg': 'success',
        'links':[
            {
                'rel':'return to original post',
                'href':f'{url_for("game.post_page",game_title=game_title,post_id=post_id)}'
            }
        ]
    }),200

@game.route('/<string:game_title>/<int:post_id>/<string:comment_parent_id>/<string:comment_id>/update_response',methods=['PATCH'])
@token_required
def update_response(game_title,post_id,comment_parent_id,comment_id):
    user=get_current_user()
    #user=User.query.get(1)
    comment=Comment.query.filter_by(comment_uuid=comment_id).filter_by(comment_parent_uuid=comment_parent_id).first()
    comment_parent=Comment.query.filter_by(comment_uuid=comment_parent_id).first()
    res={}
    res['links']=[
        {
            'rel': 'return to original post',
            'href': f'{url_for("game.post_page", game_title=game_title, post_id=post_id)}'
        }
    ]
    if comment.author!=user:
        res['msg']='you are not the author of this comment'
        return jsonify(res),400
    if not request.json.get('comment_text'):
        res['msg'] ='missing comment_text'
        return jsonify(res),400
    responses=table.query(
        KeyConditionExpression=Key('comment_id').eq(comment_parent_id)
    )['Items'][0]['responses']
    #print(responses)
    for response in responses:
        if response['comment_id']==comment_id:
            response['comment_text']=request.json.get('comment_text')
            response['version_id']=str(uuid4())
            break
    table.update_item(
        Key={
            'comment_id':comment_parent_id,
            'email':comment_parent.author.email
        },
        UpdateExpression='SET responses=:val',
        ExpressionAttributeValues={
            ':val':responses
        }
    )
    res['msg'] ='success'
    return jsonify(res),200

@game.route('/<string:game_title>/<int:post_id>/<string:comment_parent_id>/<string:comment_id>/delete_response',methods=['DELETE'])
@token_required
def delete_response(game_title,post_id,comment_parent_id,comment_id):
    user=get_current_user()
    #user=User.query.get(1)
    comment=Comment.query.filter_by(comment_uuid=comment_id).filter_by(comment_parent_uuid=comment_parent_id).first()
    comment_parent=Comment.query.filter_by(comment_uuid=comment_parent_id).first()
    res={}
    res['links']=[
        {
            'rel': 'return to original post',
            'href': f'{url_for("game.post_page", game_title=game_title, post_id=post_id)}'
        }
    ]
    if comment.author!=user:
        res['msg']='you are not the author of this comment'
        return jsonify(res),400
    db.session.delete(comment)
    db.session.commit()
    responses=table.query(
        KeyConditionExpression=Key('comment_id').eq(comment_parent_id)
    )['Items'][0]['responses']
    for i in range(len(responses)):
        if responses[i]['comment_id']==comment_id:
            responses=responses[:i]+responses[i+1:]
            break
    table.update_item(
        Key={
            'comment_id':comment_parent_id,
            'email':comment_parent.author.email
        },
        UpdateExpression='SET responses=:val',
        ExpressionAttributeValues={
            ':val':responses
        }
    )
    res['msg']='success'
    return jsonify(res),200



@game.route('/<string:game_title>/follow',methods=['POST'])
@token_required
def follow(game_title):
    user=get_current_user()
    game=Game.query.filter_by(title=game_title).first()
    res={}
    res['links']=[
        {
            'rel': 'game home page',
            'href': f'{url_for("game.home")}'
        },
        {
            'rel':f'{game_title}',
            'href':f'{url_for("game.game_posts",game_title=game_title)}'
        },
    ]
    if not user:
        res['msg']='user not found'
        return jsonify(res),404
    if not game:
        res['msg']='game not found'
        return jsonify(res),404
    if game in user.following_games:
        res['msg']='game already followed'
        return jsonify(res),200
    user.following_games.append(game)
    db.session.commit()
    res['msg']='game successfully followed'
    return jsonify(res),200

@game.route('/<string:game_title>/unfollow',methods=['POST'])
@token_required
def unfollow(game_title):
    user=get_current_user()
    game = Game.query.filter_by(title=game_title).first()
    res={}
    res['links']=[
        {
            'rel': 'game home page',
            'href': f'{url_for("game.home")}'
        },
        {
            'rel':f'{game_title}',
            'href':f'{url_for("game.game_posts",game_title=game_title)}'
        },
    ]
    if not user:
        res['msg']='user not found'
        return jsonify(res),404
    if not game:
        res['msg']='game not found'
        return jsonify(res),404
    if game not in user.following_games:
        res['msg']='you did not follow this game'
        return jsonify(res),400

    user.following_games.remove(game)
    db.session.commit()
    res['msg']=f'{game_title} successfully unfollowed'
    return jsonify(res),200






