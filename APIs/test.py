from flask import Blueprint,jsonify

test=Blueprint('test',__name__)

@test.route('/home')
def home():
    return jsonify({'msg':'this is test home page'})