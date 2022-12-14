import json
import requests
from django.core.exceptions import ValidationError

from user_manager.models import App, UserCache

ENDPOINT = 'novonordiskco.auth0.com'
CLIENT_ID = 'gS1tvn8zGmF3pcDrwmEtWOixPe846ATL'
CLIENT_SECRET = 'HfFfYLGDVh_VsdQYRxq9vVj7jGKVZh7SGSwXN32bkCFxRSntp8PiL1L-xVMOp1Mb'
AUDIENCE = 'https://novonordiskco.auth0.com/api/v2/'
GRANT_TYPE = 'client_credentials'

DEFAULT_DB_CONNECTION = 'NovoUsers'
DEFAULT_CONNECTION_ID = 'con_Vr8gcJCObeX43qbu'

TOKEN_API = '/oauth/token'


APP_ENDPOINT_GET_DATA = '/get-app-data'
APP_ENDPOINT_CREATE_USER = '/create-user'
APP_ENDPOINT_DELETE_USER = '/delete-user'


def get_token(no_scopes=False):
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'audience': AUDIENCE,
        'grant_type': GRANT_TYPE,
    }

    if no_scopes:
        payload['scope'] = []

    full_url = f"https://{ENDPOINT}{TOKEN_API}"
    response = requests.post(full_url, json=payload)

    json_response = json.loads(response.text)
    return json_response.get('access_token', None)


def authorized_request(method, url, payload=None, token=None):
    if not token:
        token = get_token()

    headers = {'authorization': 'Bearer ' + token}

    if method == 'GET':
        response = requests.get(url, payload, headers=headers)
    elif method == 'POST':
        response = requests.post(url, json=payload, headers=headers)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers)
    elif method == 'PATCH':
        response = requests.patch(url, json=payload, headers=headers)
    else:
        return 'INVALID METHOD', 0

    return response.text, response.status_code


def auth0_request(method, url, payload=None):
    full_url = f"https://{ENDPOINT}{url}"

    return authorized_request(method, full_url, payload)


def get_all_users():
    fields = 'user_id,username,email,user_metadata,app_metadata'
    page = 0
    limit = 100
    length = 100

    users = []

    while length == limit:
        result, status = auth0_request(
            'GET', f'/api/v2/users?fields={fields}&search_engine=v3&page={page}&per_page={limit}&include_totals=true'
        )
        page += 1
        if status == 200:
            json_data = json.loads(result)
            limit = json_data['limit']
            length = json_data['length']
            users += json_data['users']
        else:
            pass

    cache, c = UserCache.objects.get_or_create(id=1)
    cache.users_json = users
    cache.save()

    return users


def get_all_users_cached():
    cache: UserCache = UserCache.objects.filter(users_json__isnull=False).first()
    if cache:
        return cache.users_json
    else:
        return None


def clear_cache():
    cache: UserCache = UserCache.objects.filter(users_json__isnull=False).first()
    if cache:
        cache.users_json = None
        cache.save()


def get_user_by_user_id(user_id):
    fields = 'user_id,username,email,email_verified,user_metadata,app_metadata'
    return auth0_request('GET', f'/api/v2/users/{user_id}?fields={fields}')


def create_user(data):
    return auth0_request('POST', '/api/v2/users', payload=data)


def patch_user(data, user_id):
    return auth0_request('PATCH', f'/api/v2/users/{user_id}', payload=data)


def delete_user(user_id):
    return auth0_request('DELETE', f'/api/v2/users/{user_id}')


def request_password_reset(username, email):
    data = {
        'client_id': CLIENT_ID, 'email': email, 'connection': DEFAULT_DB_CONNECTION, 'username': username
    }
    url = "https://novonordiskco.auth0.com/dbconnections/change_password"

    response = requests.request("POST", url, json=data)

    return response.text, response.status_code


def get_app_data(instance):
    token = get_token(no_scopes=True)
    app_data_response, code = authorized_request('GET', instance.endpoint + APP_ENDPOINT_GET_DATA, token=token)
    if code != 200:
        raise ValidationError('Endpoint is not configured properly.')

    app_data = json.loads(app_data_response)
    try:
        instance.app_name = app_data['name']
        instance.app_id = app_data['id']
        instance.roles = ','.join(app_data['roles'])
    except (KeyError, TypeError):
        raise ValidationError(
            'Endpoint get-app-data must return a JSON with the following structure:'
            ' {"id": "string", "name": "string", "roles": ["string", "string", ...]}.\n'
            'Received: '+app_data_response
        )

    return instance


def update_user_apps(user_json, original_user_json=None):
    user_permissions = user_json['app_metadata']['permissions']
    to_remove_apps = set()
    token = get_token(no_scopes=True)
    errors = []

    if original_user_json:
        old_permissions = original_user_json['app_metadata']['permissions']

        for op in old_permissions:
            to_remove_apps.add(op['app'])

    for app_dict in user_permissions:
        try:
            app = App.objects.get(app_id=app_dict['app'])
            data = {
                'username': user_json['username'],
                'email': user_json['email'],
                'role': app_dict['role'],
                'user_metadata': user_json['user_metadata']
            }
            try:
                authorized_request('POST', app.endpoint + APP_ENDPOINT_CREATE_USER, payload=data, token=token)
            except:
                errors.append(f'No fue posible actualizar "{app.app_name}": Error HTTP.')
            try:
                to_remove_apps.remove(app.app_id)
            except KeyError:
                pass

        except App.DoesNotExist:
            pass

    for app_id in to_remove_apps:
        try:
            app = App.objects.get(app_id=app_id)
            data = {'username': user_json['username']}
            authorized_request('POST', app.endpoint + APP_ENDPOINT_DELETE_USER, payload=data, token=token)
        except App.DoesNotExist:
            pass
    return errors


def update_cached_user(user_id, app_metadata, user_metadata):
    cache = UserCache.objects.first()
    if not cache:
        return
    users = cache.users_json
    changed = False

    for u in users:
        if u.get('user_id') == user_id:
            u['app_metadata'] = app_metadata
            u['user_metadata'] = user_metadata
            changed = True
            break

    if changed:
        cache.users_json = users
        cache.save()
