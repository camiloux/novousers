import json
import requests

ENDPOINT = 'novonordiskco.auth0.com'
CLIENT_ID = 'gS1tvn8zGmF3pcDrwmEtWOixPe846ATL'
CLIENT_SECRET = 'HfFfYLGDVh_VsdQYRxq9vVj7jGKVZh7SGSwXN32bkCFxRSntp8PiL1L-xVMOp1Mb'
AUDIENCE = 'https://novonordiskco.auth0.com/api/v2/'
GRANT_TYPE = 'client_credentials'

DEFAULT_DB_CONNECTION = 'NovoUsers'
DEFAULT_CONNECTION_ID = 'con_Vr8gcJCObeX43qbu'

TOKEN_API = '/oauth/token'

API_ENDPOINT = ''


def get_token():
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'audience': AUDIENCE,
        'grant_type': GRANT_TYPE,
    }

    full_url = f"https://{ENDPOINT}{TOKEN_API}"
    response = requests.post(full_url, json=payload)

    json_response = json.loads(response.text)
    return json_response.get('access_token', None)


def auth_request(method, url, payload=None):
    token = get_token()
    headers = {'authorization': 'Bearer ' + token}

    full_url = f"https://{ENDPOINT}{url}"

    if method == 'GET':
        response = requests.get(full_url, payload, headers=headers)
    elif method == 'POST':
        response = requests.post(full_url, json=payload, headers=headers)
    else:
        return 'INVALID METHOD', 0

    return response.text, response.status_code


def get_all_users():
    fields = 'user_id,username,email,user_metadata,app_metadata'
    return auth_request('GET', f'/api/v2/users?fields={fields}')


def get_user_by_username(user_id):
    fields = 'user_id,username,email,email_verified,user_metadata,app_metadata'
    return auth_request('GET', f'/api/v2/users/{user_id}?fields={fields}')


def create_user(data):
    return auth_request('POST', '/api/v2/users', payload=data)


def patch_user(data, user_id):
    return auth_request('PATCH', f'/api/v2/users/{user_id}', payload=data)


def delete_user(user_id):
    return auth_request('DELETE', f'/api/v2/users/{user_id}')


def request_password_reset(username, email):
    data = {
        'client_id': CLIENT_ID, 'email': email, 'connection': DEFAULT_DB_CONNECTION, 'username': username
    }
    url = "https://novonordiskco.auth0.com/dbconnections/change_password"

    response = requests.request("POST", url, json=data)

    return response.text, response.status_code
