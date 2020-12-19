from flask import Blueprint,request,jsonify,url_for,session,redirect
from modules import bcrypt,db,mail,application
from models import User
from flask_mail import Message
from utils import token_required,get_current_user
import jwt
from oauthlib.oauth2 import WebApplicationClient
import requests
from validate_email import validate_email

from smartystreets_python_sdk import StaticCredentials, ClientBuilder
from smartystreets_python_sdk.us_autocomplete import Lookup as AutocompleteLookup


import os
import json
import random
import string

# GOOGLE_CLIENT_ID=os.getenv('GOOGLE_CLIENT_ID')
# GOOGLE_CLIENT_SECRET=os.getenv('GOOGLE_CLIENT_SECRET')
# GOOGLE_DISCOVERY_URL=("https://accounts.google.com/.well-known/openid-configuration")

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
GOOGLE_CLIENT_ID=os.environ.get('google_client_id')
GOOGLE_CLIENT_SECRET=os.environ.get('google_client_secret')
GOOGLE_DISCOVERY_URL=("https://accounts.google.com/.well-known/openid-configuration")

'''
trying to use blueprint to make the code look nicer
we need to use blueprint.route instead of application.route
and remember to register blueprint in modules.py
the name of blueprint is in Blueprint("bp name"), usually, we set the name equal to .py filename
when use url_for("bp_name.function_name")

url_for works globally
you can access other routes in another blueprint 
like url_for(another_bp_name.function_name)
'''

'''
want to add refresh token to our app
token has shorter exp time
refresh token has longer exp time

everytime we 


'''

user=Blueprint("user",__name__,static_folder=None,template_folder=None)

client=WebApplicationClient(GOOGLE_CLIENT_ID)

@user.route('/')
def home():
    #print(request.headers)
    user=get_current_user()
    res={}
    #print(request.headers.get('Authorization'))
    res['msg']='user home page'
    if user:
        res['links']=[
            {
                'rel':'profile',
                'href':f'{url_for("user.user_profile")}',
                'type':['GET','PATCH']
            },
            {
                'rel':'logout',
                'href':f'{url_for("user.logout")}',
                'type':['GET']
            }
        ]
    else:
        res['links']=[
            {
                'rel':'login',
                'href':f'{url_for("user.login")}',
                'type': ['GET','POST']
            },
            {
                'rel':'register',
                'href':f'{url_for("user.register")}',
                'type': ['GET', 'POST']
            },
            {
                'rel':'forgot_password',
                'href':f'{url_for("user.request_reset_email")}',
                'type': ['GET', 'POST']
            },
            {
                'rel':'request_activate_account',
                'href':f'{url_for("user.request_activate_account")}',
                'type': ['GET', 'POST']
            },
            # {
            #     'rel':'google_login',
            #     'href':f'{url_for("user.google_login")}'
            # }
        ]
    return jsonify(res),200


def send_activation_email(user):
    #print(user.email)
    msg=Message('User activation link',sender='hahaa@email.com',recipients=[user.email])
    msg.body=f'Dear {user.first_name+" "+user.last_name},\n' \
             f'\n' \
             f'Thank you for your registration, please clink link below to activate your account:\n' \
             f'http://127.0.0.1:3000/user/activate_account/{user.generate_token()}' \
             f'\n'\
             f'This link will expire in 30 minutes\n' \
             f'\n' \
             f'Thank you\n'
    try:
        mail.send(msg)
        return f'Account created, an activation email has been sent to {user.email}, please activate it in 30 minutes', 201
    except:
        return 'invalid email', 400

def send_reset_email(user):
    msg = Message('Password reset link', sender="afw.email.conm", recipients=[user.email])
    msg.body = f'Dear {user.first_name + " " + user.last_name},\n' \
               f'\n' \
               f'To reset your password, please click link below:\n' \
               f'http://127.0.0.1:3000/user/reset_password/{user.generate_token()}\n' \
               f'\n' \
               f'This link will expire in 30mins'
    try:
        mail.send(msg)
        return f'Account created, an activation email has been sent to {user.email}, please activate it in 30 minutes',201
    except:
        return 'invalid email', 400

def generate_random_password(n=8):
    return ''.join(random.choice(string.ascii_letters) for _ in range(n))

def send_random_password_email(user,random_password):
    msg=Message('Thank you for logging in using social account',sender="afw.email.conm",recipients=[user.email])
    msg.body=f'Dear {user.first_name+" "+user.last_name},\n' \
             f'\n' \
             f'A random password is generated for your account: {random_password}\n' \
             f'You can go to link below to change password: \n' \
             f'http://127.0.0.1:3000/user/forgot_password' \
             f'\n' \
             f'Thank you'
    mail.send(msg)

@user.route('/address_auto_complete',methods=['GET'])
def address_auto_complete():
    auth_id = os.environ.get('smartystreets_id')
    auth_token = os.environ.get('smartystreets_token')
    credentials = StaticCredentials(auth_id, auth_token)
    client = ClientBuilder(credentials).build_us_autocomplete_api_client()
    if not request.args:
        return jsonify({'msg': 'Missing address'}),400
    address=request.args.get('address')
    if not address:
        return jsonify({'msg': 'Missing address'}),400
    lookup = AutocompleteLookup(address)
    client.send(lookup)
    return jsonify({'suggestions':[suggestion.text for suggestion in lookup.result]}),200


@user.route('/register',methods=['GET','POST'])
def register():
    res = {}
    res['fields required'] = ['first_name', 'last_name', 'email', 'password','address']
    res['links']=[
        {
            'rel': 'login',
            'href': f'{url_for("user.login")}',
            'type': ['GET', 'POST']
        },
        {
            'rel':'user home page',
            'href':f'{url_for("user.home")}',
            'type': ['GET']
        }

    ]
    if request.method=='GET' or request.json==None:
        return jsonify(res),200
    else:
        #res={}
        res['fields required']=['first_name','last_name','email','password']
        first_name=request.json.get('first_name')
        last_name=request.json.get('last_name')
        email=request.json.get('email')
        password=request.json.get('password')
        address=request.json.get('address')
        if not first_name:
            res['msg']='Missing first_name'
            return jsonify(res),400
        if not last_name:
            res['msg']='Missing last_name'
            return jsonify(res),400
        if not password:
            res['msg']='Missing password'
            return jsonify(res),400
        if not email:
            res['msg']='Missing email'
            return jsonify(res),400
        if not address:
            res['msg']='Missing address'
            return jsonify(res),400
        else:
            user=User.query.filter_by(email=email).first()
            if user:
                res['msg']='This email has already been taken, please choose another one'
                return jsonify(res),400
        hashed_password=bcrypt.generate_password_hash(password)
        user=User(first_name=first_name,last_name=last_name,email=email,password=hashed_password,address=address)
        if validate_email(email):
            db.session.add(user)
            db.session.commit()
            msg, code = send_activation_email(user)
            res['msg'] = msg
            return jsonify(res), code
        else:
            res['msg']='invalid email'
            return jsonify(res), 400




@user.route('/activate_account/<string:token>')
def activate_account(token):
    res={}
    res['links']=[
        {
            'rel':'user home page',
            'href':f'{url_for("user.home")}',
            'type': ['GET']
        }
    ]
    try:
        data=User.verify_token(token)
        #print(data)
        user = User.query.get(data['user_id'])

        user.status = 'ACTIVATED'
        db.session.commit()
        res['msg']=f'{user.email} activated'
        res['links']+=[
            {
                'rel': 'login',
                'href': f'{url_for("user.login")}',
                'type': ['GET', 'POST']
            }
        ]
        return jsonify(res),200
    except:
        res['msg']='token expired or invalid'
        res['links']+=[
            {
                'rel': 'activate account',
                'href': f'{url_for("user.request_activate_account")}',
                'type': ['GET']
            }
        ]
        return jsonify(res), 400



@user.route('/request_activate_account',methods=['GET','POST'])
def request_activate_account():
    res={}
    res['fields required']=['email']
    res['links']=[
        {
            'rel':'user home page',
            'href':f'{url_for("user.home")}',
            'type': ['GET']
        },
        {
            'rel':'request activate email',
            'href':f'{request.path}',
            'type': ['GET']
        }
    ]
    user=get_current_user()
    if user:
        res['msg']='your account has already benn activated'
        return jsonify(res),400
    if request.method=='GET':
        res['msg']='send POST request with your email to require activation email'
        return jsonify(res),200
    elif request.method=='POST':
        email=request.json.get('email')
        if not email:
            res['msg']='Missing email'
        user=User.query.filter_by(email=email).first()
        if not user:
            res['msg']='This email is not linked to any account'
            res['links']+=[
                {
                    'rel':'register',
                    'href':f'{url_for("user.register")}',
                    'type': ['GET', 'POST']
                }
            ]
            return jsonify(res),400
        if user.status=='ACTIVATED':
            res['msg']='your account has already benn activated'
            return jsonify(res),400
        send_activation_email(user)
        res['msg']='Email sent'
        return jsonify(res),200



@user.route('/login',methods=['GET','POST'])
def login():
    #print(request.json)
    user=get_current_user()
    res={}
    res['fields required']=['email','password']
    res['success']=False
    res['links'] = [
        {
            'rel': 'user home page',
            'href': f'{url_for("user.home")}',
            'type': ['GET']
        }
    ]
    if user:
        res['msg']='you already logged in'
        return jsonify(res),200
    #res['msg']='login failed'
    if request.method=='GET' or not request.json:
        #session['msg']='dummy message'
        return jsonify(res),200
    else:
        email=request.json.get('email')
        password=request.json.get('password')
        if not email:
            res['error']='Missing email'
            return jsonify(res), 400
        if not password:
            res['error']='Missing password'
            return jsonify(res), 400
        user=User.query.filter_by(email=email).first()
        if not user:
            res['error']='Email not found'
            res['link']=[
                {
                    'rel':'register',
                    'href':f'{url_for("user.register")}',
                    'type': ['GET', 'POST']
                }
            ]
            return jsonify(res),400
        if not bcrypt.check_password_hash(user.password,password):
            res['error']='Wrong password'
            return jsonify(res),401
        if user.status=='PENDING':
            res['error']='please activate your account first, check the activation email'
            return jsonify(res),400
        res['msg']='login success'
        res['success']=True
        token=user.generate_token(15)
        res['token']=token
        res['token expiry time']=15*60
        res['refresh_token']=user.generate_token(60)
        res['refresh_token expiry time']=60*60
        #print(jwt.decode(res['token'],application.config['SECRET_KEY']))
        #session['token']=token
        return jsonify(res),200

'''
so here we are expecting front end to call this endpoint when current token has expired or nearly expired
provide the refresh_token generated in first login
if refresh_token also expired, just let user re-login 
'''
@user.route('/refresh_token',methods=['POST'])
def refresh_token():
    x=request.headers.get('Authorization').split(' ')
    if len(x)!=2:
        return jsonify({'msg':'you need to provide refresh_token'}),400
    token_type,token=x
    if token_type!='refresh_token':
        return jsonify({
            'msg':'you need to provide refresh_token'
        }),400
    try:
        data=jwt.decode(token,application.config['SECRET_KEY'])
        user_id=data['user_id']
        user=User.query.get(user_id)
        return jsonify({
            'msg':'token refreshed,save it',
            'token':user.generate_token(15),
            'token expiry time':15*60,
            'links':[
                {
                    'rel': 'home',
                    'href': f'{url_for("user.home")}'
                }
            ]
        }),200
    except:
        return jsonify({
            'msg':'refresh token expired, need to login first',
            'links':[
                {
                    'rel':'login',
                    'href':f'{url_for("user.login")}'
                },
                {
                    'rel':'home',
                    'href':f'{url_for("user.home")}'
                }
        ]
        }),440




# @user.route('/google_login')
# def google_login():
#     #print(GOOGLE_CLIENT_ID)
#     google_provide_config=requests.get(GOOGLE_DISCOVERY_URL).json()
#     authorization_endpoint=google_provide_config['authorization_endpoint']
#     request_uri=client.prepare_request_uri(
#         authorization_endpoint,
#         redirect_uri=request.base_url+'/callback',
#         scope=['openid','email','profile']
#     )
#     #return jsonify({'msg':'dummy data'}),200
#     return redirect(request_uri)

@user.route('/google_login',methods=['POST'])
def google_login():
    res = {}
    if not request.json:
        res['msg']='post body is required, email,first_name, last_name',400
    #print(request.json)
    email=request.json.get('email')
    first_name=request.json.get('first_name')
    last_name=request.json.get('last_name')
    if not email:
        res['msg']='missing email'
        return jsonify(res),400
    if not first_name:
        res['msg']='missing first_name'
        return jsonify(res),400
    if not last_name:
        res['msg']='missing last_name'
        return jsonify(res),400

    possible_user=User.query.filter_by(email=email).first()
    if possible_user:
        res['msg']='this email already exists in our database, we will login this account,save the token'
        res['token'] = possible_user.generate_token(60)
        res['token expiry time'] = 60 * 60
        res['refresh_token'] = possible_user.generate_token(120)
        res['refresh_token expiry time'] = 120 * 60
        return jsonify(res),200
    else:
        random_password=generate_random_password(8)
        hashed_password=bcrypt.generate_password_hash(random_password)
        new_user=User(email=email,first_name=first_name,last_name=last_name,status='ACTIVATED',password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        send_random_password_email(new_user,random_password)
        res['msg']='a new account based on your google account is created, an email has been sent to you with your initial password, you can change it later'
        res['token'] = new_user.generate_token(60)
        res['token expiry time'] = 60 * 60
        res['refresh_token'] = new_user.generate_token(120)
        res['refresh_token expiry time'] = 60 * 60
        return jsonify(res),200




    res['msg']='test google login'
    return jsonify(res),200







# @user.route('/google_login/callback')
# def google_login_callback():
#     code=request.args.get('code')
#     google_provide_config = requests.get(GOOGLE_DISCOVERY_URL).json()
#     token_endpoint=google_provide_config['token_endpoint']
#     token_url,headers,body=client.prepare_token_request(
#         token_endpoint,
#         authorization_response=request.url,
#         redirect_url=request.base_url,
#         code=code,
#     )
#
#     token_response=requests.post(
#         token_url,
#         headers=headers,
#         data=body,
#         auth=(GOOGLE_CLIENT_ID,GOOGLE_CLIENT_SECRET),
#     )
#     #print(body)
#     client.parse_request_body_response(json.dumps(token_response.json()))
#     userinfo_endpoint=google_provide_config['userinfo_endpoint']
#     uri,headers,body=client.add_token(userinfo_endpoint)
#     userinfo_response=requests.get(uri,headers=headers,data=body)
#     if userinfo_response.json().get('email_verified'):
#         email=userinfo_response.json()['email']
#         first_name=userinfo_response.json()['given_name']
#         last_name=userinfo_response.json()['family_name']
#         user=User.query.filter_by(email=email).first()
#         if user:
#             token = user.generate_token()
#             session['token'] = token
#             return redirect(url_for("user.login"))
#         else:
#             random_password=generate_random_password()
#             user=User(first_name=first_name,last_name=last_name,email=email,password=bcrypt.generate_password_hash(random_password),status='ACTIVATED')
#             db.session.add(user)
#             db.session.commit()
#             send_random_password_email(user,random_password)
#             response=requests.post(url_for("user.login",_external=True),data={'email':email,'password':random_password})
#             #print(response)
#             return redirect(url_for('user.home'))
#     else:
#         return jsonify({
#             'msg': 'your email is not verified',
#             'links':[
#                 {
#                     'rel': 'user home page',
#                     'href':f'{url_for("user.home")}'
#                 }
#             ]
#         }),400

@user.route('/logout')
@token_required
def logout():
    # session.pop('token')
    return jsonify({
        'msg': 'logged out',
        'links':[
            {
                'rel':'user home page',
                'href':f'{url_for("user.home")}',
                'type': ['GET']
            }
        ]
    })

@user.route('/profile',methods=['GET','PATCH'])
@token_required
def user_profile():
    # token=session.get('token')
    token_type,token=request.headers.get('Authorization').split(' ')
    data=jwt.decode(token,application.config['SECRET_KEY'])
    user=User.query.get(data['user_id'])
    res= {'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'status': user.status,'address':user.address,
          'links': [
              {
                  'rel': 'user home page',
                  'href': f'{url_for("user.home")}',
                  'type': ['GET']
              },
              {
                  'rel': 'logout',
                  'href': f'{url_for("user.logout")}',
                  'type': ['GET']
              }
          ], 'posts': [{
            'title': post.title,
            'abstract': post.content[:10] + "...",
            'href': f'{url_for("game.post_page", game_title=post.game.title, post_id=post.id)}'
        } for post in user.posts]}

    if request.method=='GET':
        return jsonify(res),200
    else:
        first_name=request.json.get('first_name')
        last_name=request.json.get('last_name')
        address=request.json.get('address')
        if not first_name:
            res['msg']='missing first name'
            return jsonify(res),400
        if not last_name:
            res['msg']='missing last name'
            return jsonify(res),400
        if not address:
            res['msg']='missing address'
            return jsonify(res),400
        user.first_name=first_name
        user.last_name=last_name
        user.address=address
        db.session.commit()
        res['msg']='profile updated'
        return jsonify(res),200

@user.route('/view_profile/<int:user_id>')
def view_profile(user_id):
    user=User.query.get(user_id)
    res={}
    res['links']=[
        {
            'rel':'user home page',
            'href':f'{url_for("user.home")}',
            'type': ['GET']
        }
    ]
    if not user:
        res['msg']='user not found'
        return jsonify(res),404
    res['first_name']=user.first_name
    res['last_name']=user.last_name
    res['email']=user.email
    res['posts']=[{
        'title':post.title,
        'abstract':post.content[:10]+"...",
        'href':f'{url_for("game.post_page",game_title=post.game,post_id=post.id)}'
    } for post in user.posts]
    return jsonify(res),200


@user.route('/forgot_password',methods=['GET','POST'])
def request_reset_email():
    user=get_current_user()
    res={}
    res['fields required']=['email']
    res['links']=[
        {
            'rel': 'user home page',
            'href': f'{url_for("user.home")}',
            'type': ['GET']
        }
    ]
    if user:
        res['msg']='you already logged in'
        return jsonify(res),400
    if request.method=='GET':
        res['msg']='use POST request including your email'
        res['links']+=[
            {
                'rel': 'request reset password',
                'href': f'{request.path}',
                'type': ['GET', 'POST']
            }
        ]
        return jsonify(res),200
    elif request.method=='POST':
        email=request.json.get('email')
        if not email:
            res['msg']='Missing email'
            return jsonify(res),400
        user=User.query.filter_by(email=email).first()
        if not user:
            res['msg']='This email is not linked to any account'
            res['links']+=[
                {
                    'rel': 'request reset password',
                    'href': f'{request.path}',
                    'type': ['GET', 'POST']
                },
                {
                    'rel':'create a new account',
                    'href':f'{url_for("user.register")}',
                    'type': ['GET', 'POST']
                }
            ]
            return jsonify(res),404
        res['msg']='rest email send, link will expire in 30 mins'
        send_reset_email(user)
        return jsonify(res),200


@user.route('/reset_password/<string:token>',methods=['GET','POST'])
def reset_password(token):
    #token=request.args.get('token')
    res={}
    res['fields required']=['password','confirm_password']
    user = get_current_user()
    if user:
        res['msg']='you already logged in'
        res['links']=[
            {
                'rel':'user home page',
                'href':f'{url_for("user.home")}',
                'type': ['GET']
            }
        ]
        return jsonify(res),400

    try:
        data=jwt.decode(token,application.config['SECRET_KEY'])
        user=User.query.get(data['user_id'])
        if request.method=='GET':
            res['msg']='send POST request with new password'
            return jsonify(res),200
        elif request.method=='POST':
            #print(request.json)
            if not request.json or not request.json.get('password') or not request.json.get('confirm_password'):
                res['msg']='Missing post body, password or confirm password'
                return jsonify(res),400
            password=request.json.get('password')
            confirm_password=request.json.get('confirm_password')
            if not password:
                res['password']='Missing password'
                return jsonify(res),400
            if not confirm_password:
                res['confirm_password']='Missing confirm_password'
                return jsonify(res),400
            if password!=confirm_password:
                res['msg']='password and confirm_password does not match!'
                return jsonify(res),400
            if bcrypt.check_password_hash(user.password,password):
                res['msg']='new password cannot be the same as old password'
                return jsonify(res),400
            user.password=bcrypt.generate_password_hash(password)
            db.session.commit()
            res['msg']='password updated'
            res['links']=[
                {
                    'rel':'login',
                    'href':f'{url_for("user.login")}',
                    'type': ['GET', 'POST']
                }
            ]
            return jsonify(res),200

    except:
        return jsonify({
            'msg':'link expired, please request another rest link',
            'links':[
                {
                    'rel': 'request rest email',
                    'href':f'{url_for("user.request_reset_email",_external=True)}',
                    'type': ['GET', 'POST']
                }
            ]
        }),440















