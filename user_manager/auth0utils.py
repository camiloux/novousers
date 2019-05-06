import http.client
import json

ENDPOINT = 'novonordiskco.auth0.com'
CLIENT_ID = 'gS1tvn8zGmF3pcDrwmEtWOixPe846ATL'
CLIENT_SECRET = 'HfFfYLGDVh_VsdQYRxq9vVj7jGKVZh7SGSwXN32bkCFxRSntp8PiL1L-xVMOp1Mb'
AUDIENCE = 'https://novonordiskco.auth0.com/api/v2/'
GRANT_TYPE = 'client_credentials'

DEFAULT_DB_CONNECTION = 'NovoUsers'

TOKEN_API = '/oauth/token'

API_ENDPOINT = ''


def get_token():
    conn = http.client.HTTPSConnection(ENDPOINT)
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'audience': AUDIENCE,
        'grant_type': GRANT_TYPE,
    }
    headers = {'content-type': 'application/json'}

    conn.request('POST', TOKEN_API, json.dumps(payload), headers)

    res = conn.getresponse()
    data = res.read()
    json_response = json.loads(data.decode('utf-8'))
    return json_response.get('access_token', None), conn


def auth_request(method, url, payload=None):
    token, conn = get_token()
    headers = {'authorization': 'Bearer ' + token}
    if payload:
        headers.update({'content-type': 'application/json'})
    conn.request(method, url, body=payload, headers=headers)

    res = conn.getresponse()
    data = res.read()

    return data.decode('utf-8')


def get_all_users():
    fields = 'user_id,username,email'
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
