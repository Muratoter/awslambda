import os

import boto3
from flask import Flask, jsonify, make_response, request

app = Flask(__name__)


dynamodb = boto3.resource('dynamodb')

if os.environ.get('IS_OFFLINE'):
    print("is offline")
    dynamodb = boto3.resource('dynamodb', region_name='localhost', endpoint_url='http://localhost:8000')


USERS_TABLE = dynamodb.Table(os.environ['USERS_TABLE'])


@app.route('/users/<string:user_id>')
def get_user(user_id):
    result = USERS_TABLE.get_item(
        Key={'userId': user_id}
    )
    item = result.get('Item')
    print(result)
    if not item:
        return jsonify({'error': 'Could not find user with provided "userId"'}), 404
    return jsonify(
        {'userId': item.get('userId'), 'name': item.get('name')}
    )

@app.route('/users/', methods=['GET'])
def get_users():
    result = USERS_TABLE.scan()
    print("result: ",result)
    items = result.get('Items')
    print(items)
    
    return jsonify(items)

@app.route('/users', methods=['POST'])
def create_user():
    user_id = request.json.get('userId')
    name = request.json.get('name')
    if not user_id or not name:
        return jsonify({'error': 'Please provide both "userId" and "name"'}), 400

    USERS_TABLE.put_item(Item={'userId': user_id, 'name': name})

    return jsonify({'userId': user_id, 'name': name})


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
