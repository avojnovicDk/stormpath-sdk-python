import base64

from unittest import TestCase, main
from six import u
try:
    from mock import patch, MagicMock, PropertyMock
except ImportError:
    from unittest.mock import patch, MagicMock, PropertyMock

from stormpath.api_auth import authenticate, AccessToken
from stormpath.error import Error as StormpathError
from stormpath.resources import Account
from stormpath.resources.base import StatusMixin

FAKE_CLIENT_ID = 'fake_client_id'
FAKE_CLIENT_SECRET = 'fake_client_secret'


class ApiAuthTest(TestCase):

    def test_basic_api_auth(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
                id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        basic_auth = base64.b64encode("{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))

        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        result = authenticate(app, allowed_scopes, http_method, uri, body, headers)
        self.assertIsNotNone(result)
        self.assertIsNone(result.token)
        self.assertIsNotNone(result.api_key)

    def test_basic_api_auth_unicode_and_locations(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
                id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        basic_auth = base64.b64encode(
            "{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))

        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {}
        headers = {'Authorization': u('Basic ') + basic_auth.decode('utf-8')}

        allowed_scopes = ['test1']

        result = authenticate(
            app, allowed_scopes, http_method, uri, body, headers, ['header'])
        self.assertIsNotNone(result)
        self.assertIsNone(result.token)
        self.assertIsNotNone(result.api_key)

    def test_basic_api_auth_with_generating_bearer_token(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
                id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        basic_auth = base64.b64encode("{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))

        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        result = authenticate(app, allowed_scopes, http_method, uri, body, headers)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.api_key)
        self.assertIsNotNone(result.token)
        self.assertEquals(result.token.scopes, ['test1'])

    def test_basic_api_auth_with_invalid_scope_no_token_get_generated(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
                id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        basic_auth = base64.b64encode("{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))

        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'invalid_scope'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        result = authenticate(app, allowed_scopes, http_method, uri, body, headers)
        self.assertIsNotNone(result)
        self.assertIsNone(result.token)

    def test_basic_api_auth_invalid_credentials(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: None

        app.api_keys = api_keys

        basic_auth = base64.b64encode("invalid_client_id:invalid_client_secret".encode('utf-8'))

        uri = 'https://example.com/get'
        http_method = 'GET'
        # body = {}
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        result = authenticate(app, allowed_scopes, http_method, uri, body, headers)
        self.assertIsNone(result)

    def test_bearer_api_auth(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
                id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        basic_auth = base64.b64encode("{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))

        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        result = authenticate(app, allowed_scopes, http_method, uri, body, headers)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {
                'Authorization': b'Bearer ' + token.token.encode('utf-8')
                }

        result = authenticate(app, allowed_scopes, http_method, uri, body, headers)
        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_unicode(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
                id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        basic_auth = base64.b64encode(
            "{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))

        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': u('Basic ') + basic_auth.decode('utf-8')}

        allowed_scopes = ['test1']

        result = authenticate(app, allowed_scopes, http_method, uri, body, headers)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {
                'Authorization': b'Bearer ' + token.token.encode('utf-8')
                }

        result = authenticate(app, allowed_scopes, http_method, uri, body, headers)
        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_token_in_url(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
            id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET,
            status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        basic_auth = base64.b64encode(
            "{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))

        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}

        allowed_scopes = ['test1']

        result = authenticate(
            app=app, allowed_scopes=allowed_scopes, body=body, headers=headers)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        uri = 'https://example.com/get?access_token=%s' % (token.token)
        locations = ['url']

        result = authenticate(
            app=app, allowed_scopes=allowed_scopes, body={}, headers={},
            uri=uri, locations=locations)
        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_token_in_url_without_locations(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
            id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET,
            status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        basic_auth = base64.b64encode(
            "{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))

        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}

        allowed_scopes = ['test1']

        result = authenticate(
            app=app, allowed_scopes=allowed_scopes, body=body, headers=headers)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        uri = 'https://example.com/get?access_token=%s' % (token.token)

        result = authenticate(
            app=app, allowed_scopes=allowed_scopes, body={}, headers={},
            uri=uri)
        self.assertIsNone(result)

    def test_bearer_api_auth_with_token_in_body(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
            id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET,
            status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        basic_auth = base64.b64encode(
            "{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))

        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}

        allowed_scopes = ['test1']

        result = authenticate(
            app=app, allowed_scopes=allowed_scopes, body=body, headers=headers)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {'access_token': token.token}
        locations = ['body']

        result = authenticate(
            app=app, allowed_scopes=allowed_scopes, body=body, headers={},
            locations=locations)
        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_bearer_api_auth_with_token_in_body_without_locations(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
            id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET,
            status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        basic_auth = base64.b64encode(
            "{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))

        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {'Authorization': b'Basic ' + basic_auth}

        allowed_scopes = ['test1']

        result = authenticate(
            app=app, allowed_scopes=allowed_scopes, body=body, headers=headers)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {'access_token': token.token}

        result = authenticate(
            app=app, allowed_scopes=allowed_scopes, body=body, headers={})
        self.assertIsNotNone(result)
        self.assertEquals(result.token.token, token.token)

    def test_access_token_validity_expired_token(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
                id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        access_token = AccessToken(
                app=app,
                token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJIUkVGIiwiaWF0IjoxNDA1NDI5MDU5LCJleHAiOjE0MDU0MzI2NTksInN1YiI6ImZha2VfY2xpZW50X2lkIiwic2NvcGUiOiJ0ZXN0MSJ9.dNPzOg8cFxkknakTAccRfcGoRiPjn7z-M5TUacy5OTE'
                )
        self.assertFalse(access_token._is_valid())


    def test_access_token_scope_check(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
                id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        access_token = AccessToken(
                app=app,
                token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJIUkVGIiwiaWF0IjoxNDA1NDI5MDU5LCJleHAiOjE0MDU0MzI2NTksInN1YiI6ImZha2VfY2xpZW50X2lkIiwic2NvcGUiOiJ0ZXN0MSJ9.dNPzOg8cFxkknakTAccRfcGoRiPjn7z-M5TUacy5OTE'
                )
        self.assertFalse(access_token._within_scope(['fake_scope_that_the_token_doesnt_have']))

    def test_access_token_invalid_token(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
                id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        access_token = AccessToken(
                app=app,
                token='invalid_token_format'
                )
        self.assertFalse(access_token._is_valid())


    def test_valid_bearer_token_but_deleted_api_key(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
            id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET,
            status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        ds = MagicMock()
        ds.get_resource.side_effect = StormpathError(
            {'developerMessage': 'No username on account.'})
        client = MagicMock(data_store=ds)
        app.accounts.get.return_value = Account(client=client, href='account')

        basic_auth = base64.b64encode(
            "{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))

        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        result = authenticate(
            app, allowed_scopes, http_method, uri, body, headers)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {
                'Authorization': b'Bearer ' + token.token.encode('utf-8')
                }

        api_keys.get_key = lambda k, s=None: None

        result = authenticate(
            app, allowed_scopes, http_method, uri, body, headers)
        self.assertIsNone(result)

    def test_valid_bearer_token_but_disabled_api_key(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
                id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        api_keys.get_key = lambda k, s=None: MagicMock(
            id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET,
            status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys
        ds = MagicMock()
        ds.get_resource.side_effect = StormpathError(
            {'developerMessage': 'No username on account.'})
        client = MagicMock(data_store=ds)
        app.accounts.get.return_value = Account(client=client, href='account')

        basic_auth = base64.b64encode("{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))

        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'client_credentials', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        result = authenticate(app, allowed_scopes, http_method, uri, body, headers)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.token)
        token = result.token
        body = {}
        headers = {
                'Authorization': b'Bearer ' + token.token.encode('utf-8')
                }

        disabled_api_key = MagicMock(
                id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_DISABLED)
        disabled_api_key.is_enabled.return_value = False

        api_keys.get_key = lambda k, s=None: disabled_api_key

        result = authenticate(app, allowed_scopes, http_method, uri, body, headers)
        self.assertIsNone(result)

    def test_invalid_grant_type_no_token_gets_generated(self):
        app = MagicMock()
        app._client.auth.secret = 'fakeApiKeyProperties.secret'
        app.href = 'HREF'
        api_keys = MagicMock()
        api_keys.get_key = lambda k, s=None: MagicMock(
                id=FAKE_CLIENT_ID, secret=FAKE_CLIENT_SECRET, status=StatusMixin.STATUS_ENABLED)
        app.api_keys = api_keys

        basic_auth = base64.b64encode("{}:{}".format(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET).encode('utf-8'))

        uri = 'https://example.com/get'
        http_method = 'GET'
        body = {'grant_type': 'invalid_grant', 'scope': 'test1'}
        headers = {
                'Authorization': b'Basic ' + basic_auth
                }

        allowed_scopes = ['test1']

        result = authenticate(app, allowed_scopes, http_method, uri, body, headers)
        self.assertIsNotNone(result)
        self.assertIsNone(result.token)


if __name__ == '__main__':
    main()
