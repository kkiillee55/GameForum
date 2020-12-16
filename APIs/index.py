from flask import Blueprint,url_for,jsonify
from modules import application,db

'''
home page
'''

index=Blueprint("index",__name__,static_folder=None,template_folder=None)


@index.route('/')
def home():
    res={}
    res['msg']='api home'
    res['links']=[
        {
            'rel':'user',
            'href':f'{url_for("user.home",_external=True)}'
        },
        {
            'rel':'game',
            'href':f'{url_for("game.home",_external=True)}'
        }
    ]
    return jsonify(res),200