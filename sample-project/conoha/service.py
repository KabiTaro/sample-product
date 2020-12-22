from dataclasses import dataclass, field, asdict
from datetime import datetime

import json
from os import environ

from django.utils.timezone import make_aware

from django.conf import settings
from dacite import from_dict

from pytz import timezone
import requests
from requests.packages.urllib3.util.retry import Retry

from requests.adapters import HTTPAdapter

from conoha.exceptions import ConohaRequestsException, ConohaNotSpecifiedException

RETRY_STATUS_CODE = [429, 500, 502, 503, 504]
WHITELIST_METHOD = ["GET", "PUT", "POST", "DELETE"]


@dataclass
class RequestsArgs:
    url: str
    json: dict = field(default=None)
    headers: dict = field(default=None)
    data: bytes = field(default=None)


class GeneralRequests:
    def __init__(self, method: str):
        self._method = method

    def __call__(self, func):
        def _f(*args, **kwargs) -> requests.Response:
            request_args = func(*args, **kwargs)
            func_name = func.__name__
            session = requests.Session()
            retry = Retry(total=3,
                          backoff_factor=1,
                          status_forcelist=RETRY_STATUS_CODE,
                          method_whitelist=WHITELIST_METHOD
                          )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount(request_args.url, adapter)
            try:
                res = getattr(session, self._method)(**asdict(request_args))
                res.raise_for_status()
            except requests.exceptions.RequestException as re:
                raise ConohaRequestsException(
                    response=res,
                    is_retry=retry.is_retry(self._method, res.status_code),
                    message='{} is failed'.format(func_name)
                ) from re

            return res
        return _f


@dataclass
class ConohaIdentityres:
    issued_at: str
    expires: str
    id: str


@dataclass
class ConohaIdentity:
    identity_url: str
    identity_api_version: str
    tenant_id: str
    user: str
    password: str

    res: ConohaIdentityres = field(default=None, init=False)

    @property
    def request_url(self) -> str:
        return '{base_url}/{api_version}/tokens'.format(
            base_url=self.identity_url,
            api_version=self.identity_api_version
        )

    @property
    def request_param(self) -> dict:
        return {"auth": {"passwordCredentials": {
            "username": self.user,
            "password": self.password
        },
            "tenantId": self.tenant_id
        }
        }

    @property
    def is_expire(self) -> bool:
        # トークンがセットされてない場合は期限切れとして扱う
        if(self.res is None):
            return True
        _tz = timezone(settings.TIME_ZONE)
        _expire_time = datetime.strptime(
            self.res.expires, '%Y-%m-%dT%H:%M:%S%z').astimezone(tz=_tz)

        _now_time = make_aware(datetime.now())

        return _now_time.timestamp() > _expire_time.timestamp()

    def set_token(self) -> None:
        @GeneralRequests(method='post')
        def _post_identity() -> RequestsArgs:
            return RequestsArgs(
                url=self.request_url,
                json=self.request_param)

        res = _post_identity()
        self.res = from_dict(
            data_class=ConohaIdentityres,
            data=json.loads(res.text)['access']['token']
        )

        return


@dataclass
class ConohaObjectStorage:
    object_storage_url: str
    object_storage_api_version: str
    object_storage_container: str

    identity_config: ConohaIdentity

    @property
    def request_url(self) -> str:
        return '{base_url}/{api_version}/nc_{tenant_id}/{container}'.format(
            base_url=self.object_storage_url,
            api_version=self.object_storage_api_version,
            tenant_id=self.identity_config.tenant_id,
            container=self.object_storage_container
        )

    @property
    def request_header(self) -> dict:
        return {
            "Accept": "application/json",
            'X-Auth-Token': self.identity_config.res.id
        }

    def required_request_for_token(func):
        def _f(self, *args, **kwargs):
            if(self.identity_config.is_expire):
                self.identity_config.set_token()

            return func(self, *args, **kwargs)
        return _f

    @required_request_for_token
    @GeneralRequests(method='put')
    def upload_object(self, upload_image: bytes, upload_object_name: str) -> requests.Response:
        if (not upload_object_name.strip()):
            raise ConohaNotSpecifiedException('オブジェクト名が指定されていません')
        return RequestsArgs(
            url='{request_url}/{upload_object_name}'.format(
                request_url=self.request_url,
                upload_object_name=upload_object_name
            ),
            headers=self.request_header,
            data=upload_image
        )

    @required_request_for_token
    @GeneralRequests(method='put')
    def delete_object(self, delete_object_name: str) -> RequestsArgs:
        if (not delete_object_name.strip()):
            raise ConohaNotSpecifiedException('オブジェクト名が指定されていません')
        return RequestsArgs(
            url='{request_url}/{delete_object_name}'.format(
                request_url=self.request_url,
                delete_object_name=delete_object_name
            ),
            headers=self.request_header
        )

    @required_request_for_token
    @GeneralRequests(method='get')
    def get_container(self,
                      optional_header: dict = {}) -> RequestsArgs:
        return RequestsArgs(
            url=self.request_url,
            headers={**optional_header, **self.request_header}
        )

    @required_request_for_token
    @GeneralRequests(method='put')
    def create_container(self,
                         optional_header: dict = {}) -> RequestsArgs:
        return RequestsArgs(
            url=self.request_url,
            headers={**optional_header, **self.request_header}
        )

    @required_request_for_token
    @GeneralRequests(method='delete')
    def delete_container(self) -> RequestsArgs:
        return RequestsArgs(
            url=self.request_url,
            headers=self.request_header
        )

    @classmethod
    def factory(cls, container_name: str,
                tenant_id: str = environ.get('CONOHA_TENANT_ID'),
                user: str = environ.get('CONOHA_API_USER'),
                password: str = environ.get('CONOHA_API_PASSWORD')):
        if (not container_name.strip()):
            raise ConohaNotSpecifiedException('コンテナ名が指定されていません')
        _cls = from_dict(data_class=cls, data={
            'object_storage_url': 'https://object-storage.tyo1.conoha.io',
            'object_storage_api_version': 'v1',
            'object_storage_container': container_name,
            'identity_config':
                {'identity_url': 'https://identity.tyo1.conoha.io',
                 'identity_api_version': 'v2.0',
                 'tenant_id': tenant_id,
                 'user': user,
                 'password': password
                 }
        }
        )
        return _cls
