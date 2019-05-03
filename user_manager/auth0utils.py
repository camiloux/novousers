import http.client
import json

ENDPOINT = 'novonordiskco.auth0.com'
CLIENT_ID = 'gS1tvn8zGmF3pcDrwmEtWOixPe846ATL'
CLIENT_SECRET = 'HfFfYLGDVh_VsdQYRxq9vVj7jGKVZh7SGSwXN32bkCFxRSntp8PiL1L-xVMOp1Mb'
AUDIENCE = 'https://novonordiskco.auth0.com/api/v2/'
GRANT_TYPE = 'client_credentials'

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
    headers = {'content-type': "application/json"}

    conn.request('POST', TOKEN_API, json.dumps(payload), headers)

    res = conn.getresponse()
    data = res.read()
    json_response = json.loads(data.decode('utf-8'))
    return json_response.get('access_token', None), conn


def auth_request(method, url, payload=None):
    token, conn = get_token()
    headers = {'authorization': 'Bearer ' + token}
    conn.request(method, url, body=payload, headers=headers)

    res = conn.getresponse()
    data = res.read()

    return data.decode('utf-8')


def get_all_users():
    return auth_request('GET', '/api/v2/users?fields=username,email')


def get_user_by_username(username):
    return auth_request('GET', f'/api/v2/users?q=username:{username}')
