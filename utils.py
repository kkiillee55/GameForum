from functools import wraps
import jwt
from flask import request,jsonify,url_for,session
from modules import application
from models import User

'''
token required makes sure user is logged in
admin required makes sure user is admin

user token_required before admin_required
'''

'''
token required needs to be changed
instead of reading token info form session.get('token')
we are gonna read it from token=request.header.get('Authorization')
then decode token
since frontend must provide token for us
'''

def token_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):

        x=request.headers.get('Authorization').split(' ')
        if len(x)!=2:
            return jsonify({
                'msg': 'token required, please login',
                'links': [
                    {
                        'rel': 'login',
                        'href': f'{url_for("user.login")}'
                    },
                    {
                        'rel':'user home page',
                        'href':f'{url_for("user.home")}'
                    },
                ]

            }),400

        token_type,token=x
        #data=jwt.decode(token,application.config['SECRET_KEY'])
        #
        #token=request.headers.get('Authorization')
        #refresh_token=request.headers.get('RefreshToken')
        if not token:
            return jsonify({
                'msg': 'token required, please login',
                'links': [
                    {
                        'rel': 'login',
                        'href': f'{url_for("user.login")}'
                    },
                    {
                        'rel':'user home page',
                        'href':f'{url_for("user.home")}'
                    },
                ]

            }),400
        try:
            data=jwt.decode(token,application.config['SECRET_KEY'])
            user=User.query.get(data['user_id'])

            if user.status=='PENDING':
                return jsonify({
                    'msg':'please activate your account first, check the activation email'
                }),400
            return func(*args,**kwargs)
        except:
            #print("you are in herer")
            return jsonify({
                'msg': 'token expired or invalid, please re-login',
                'links':[
                    {
                        'rel':'login',
                        'href':f'{url_for("user.login")}'
                    },
                    {
                        'rel': 'user home page',
                        'href': f'{url_for("user.home")}'
                    },
                ]
            }),440
    return wrapper

#in admin required we assume token is always valid, becasue it's used after token required
def admin_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        token=request.headers.get('Authorization')
        data=jwt.decode(token,application.config['SECRET_KEY'])
        user=User.query.get(data['user_id'])
        if user.is_admin:
            return func(*args,**kwargs)

        res={}
        res['links']=[
            {
                'rel': 'home',
                'href': f'{url_for("user.home")}'
            }
        ]
        res['msg']='you are not admin, access denied'
        return jsonify(res),400
    return wrapper



'''
we also need to change it 
token=request.json.get('token')

'''
def get_current_user():
    try:
        token_type,token=request.headers.get('Authorization').split(' ')
        data=jwt.decode(token,application.config['SECRET_KEY'])
        return User.query.get(data['user_id'])
    except:
        return None