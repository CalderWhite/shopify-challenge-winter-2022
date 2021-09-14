import hashlib
import os
import secrets
import sys

from flask import Flask, jsonify, request, make_response
import psycopg2

API_VERSION = '0.1.0'
app = Flask(__name__)
ADMIN_AUTH_HASH = os.environ['ADMIN_AUTH_HASH']
PSQL_CONN_STRING = "dbname='shopify' user='flask' host='db'"

def hash_token(token):
    return hashlib.sha1(token.encode('utf-8')).hexdigest()

def verify_auth(user_id):
    token = request.headers.get('token')
    if token == None:
        return jsonify({
            'message': 'No authentication token supplied!'
        }), 401

    conn = psycopg2.connect(PSQL_CONN_STRING)
    cursor = conn.cursor()
    cursor.execute('SELECT token_hash FROM users WHERE user_id = %s', (user_id, ))

    row = cursor.fetchone()
    conn.close()
    if row is None:
        return jsonify({
            'message': 'The user [%s] does not exist!' % user_id
        }), 400

    db_token_hash = row[0]
    if db_token_hash != hash_token(token):
        return jsonify({
            'message': 'Incorrect token.'
        }), 401


def verify_auth_admin():
    token = request.headers.get('token')
    if token == None:
        return jsonify({
            'message': 'No authentication token supplied!'
        }), 401


    token_hash = hash_token(token)
    if token_hash != ADMIN_AUTH_HASH:
        return jsonify({
            'message': 'Authentication token does not have admin access.'
        }), 403


@app.route('/api/v1/users/<string:user_id>/images', methods=['POST'])
def api_create_images(user_id):
    auth_error_res = verify_auth(user_id)
    if auth_error_res is not None:
        return auth_error_res

    is_public = True
    is_private = request.headers.get('private')
    if is_private is not None and is_private.lower() == "true":
        is_public = False


    for filename in request.files.keys():
        if len(filename) > 128:
            return jsonify({
                'message': '[%s] exceeds the filename limit of 128 characters.' % filename
            }), 400

    conn = psycopg2.connect(PSQL_CONN_STRING)
    cursor = conn.cursor()
    for filename, f in request.files.items():
        data = f.read()
        try:
            cursor.execute('INSERT INTO images VALUES (%s, %s, %s, %s, %s)',
                    (user_id, filename, is_public, f.content_type, data))

            # commit each time so we don't store too much data in RAM
            conn.commit()
        except psycopg2.errors.UniqueViolation:
            conn.commit()

    return jsonify({
        'message': 'Images have been created'
    }), 200


@app.route('/api/v1/users/<string:user_id>/images/<string:image_filename>', methods=['DELETE'])
def api_delete_image(user_id, image_filename):
    auth_error_res = verify_auth(user_id)
    if auth_error_res is not None:
        return auth_error_res

    conn = psycopg2.connect(PSQL_CONN_STRING)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM images WHERE owner_id = %s AND filename = %s',
                   (user_id, image_filename))
    conn.commit()

    return jsonify({
        'message': 'Images have been deleted'
    }), 200

@app.route('/api/v1/users/<string:user_id>/images', methods=['DELETE'])
def api_delete_images(user_id):
    auth_error_res = verify_auth(user_id)
    if auth_error_res is not None:
        return auth_error_res

    body = request.get_json(force=True)

    if body is None:
        return jsonify({
            'message': "No message body."
        }), 400

    if 'images' not in body:
        return jsonify({
            'message': 'Missing "images" key.'
        }), 400

    if type(body['images']) != list:
        return jsonify({
            'message': '"images" key is not a list.'
        }), 400

    conn = psycopg2.connect(PSQL_CONN_STRING)
    cursor = conn.cursor()
    for filename in body['images']:
        cursor.execute('DELETE FROM images WHERE owner_id = %s AND filename = %s',
                       (user_id, filename))

        # commit each time so we don't store too much data in RAM
        conn.commit()

    return jsonify({
        'message': 'Images have been deleted'
    }), 200


@app.route('/api/v1/users/<string:user_id>/images/<string:image_filename>', methods=['GET'])
def api_get_image(user_id, image_filename):
    conn = psycopg2.connect(PSQL_CONN_STRING)
    cursor = conn.cursor()
    cursor.execute('SELECT is_public, content_type, data FROM images WHERE \
                            owner_id = %s AND filename = %s',
                   (user_id, image_filename))

    row = cursor.fetchone()
    if row == None:
        return jsonify({
            "message": "Image not found."
        }), 404

    is_public, content_type, data = row

    if not is_public:
        auth_error_res = verify_auth(user_id)

        if auth_error_res is not None:
            return auth_error_res

    res = make_response(bytes(data))
    res.headers.set('Content-Type', content_type)
    return res


@app.route('/api/v1/users/<string:user_id>', methods=['POST'])
def api_create_user(user_id):
    auth_error_res = verify_auth_admin()

    if auth_error_res is not None:
        return auth_error_res

    if len(user_id) > 16:
        return jsonify({
            'message': 'user_id is too long (max length 16 characters).'
        }), 400

    user_token = secrets.token_hex(32)
    user_token_hash = hash_token(user_token)

    conn = psycopg2.connect(PSQL_CONN_STRING)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users VALUES(%s, %s)', (user_id, user_token_hash))
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        return jsonify({
            'message': 'User [%s] already exists!' % user_id
        }), 500

    conn.close()

    return jsonify({
        'token': user_token
    }), 201


@app.route('/api/v1/users/<string:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    auth_error_res = verify_auth_admin()
    if auth_error_res is not None:
        return auth_error_res

    conn = psycopg2.connect(PSQL_CONN_STRING)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE user_id = %s', (user_id, ))
    conn.commit()
    conn.close()

    return jsonify({
        'message': 'The user [%s] has been deleted.' % user_id
    }), 200


@app.route('/api/v1')
def api_home():
    return jsonify({
        'version': API_VERSION,
        'status': 'OK'
    }), 200


app.run(host='0.0.0.0')
