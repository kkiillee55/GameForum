from flask import Blueprint,request,jsonify
from modules import bcrypt,db,mail,application
import requests
import boto3
from requests_aws4auth import AWS4Auth
import os
import json
search=Blueprint('search',__name__,static_folder=None,template_folder=None)



service='es'
region='us-east-2'
credentials=boto3.Session().get_credentials()
awsauth=AWS4Auth(credentials.access_key,credentials.secret_key,region,service,session_token=credentials.token)
es_host=os.environ.get('es_host')
index='comments'
type='_doc'
url=f'{es_host}/{index}/{type}/'
headers={"Content-Type": "application/json"}

@search.route('/')
def home():
    if not request.json or not request.json.get('search_text'):
        return jsonify({'msg':'search_text needed'}),400
    search_text=request.json.get('search_text')
    j={
        "query":{
            "match":{
                "comment_text":{
                    "query":f"*{search_text}*",
                    "fuzziness":"AUTO"
                }
            }
        }
    }
    # print(j)
    res = {}
    res['search_result']=[]
    hits=requests.get(url+'_search',json=j,auth=awsauth,headers=headers).json()['hits']['hits']
    for hit in hits:
        comment=hit['_source']
        temp={
            'comment_text':comment['comment_text'],
            'datetime':comment['datetime'],
            'to original post':f'/game/{comment["game_title"]}/{comment["post_id"]}'
        }
        res['search_result'].append(temp)


    #return jsonify(response.json),200
    return jsonify(res),200