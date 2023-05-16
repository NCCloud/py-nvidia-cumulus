import time
from .base import Request
from .util import url_safe


class BaseModel:
    """
    The base that each model shares
    """

    def __init__(self, client, endpoint: str) -> None:
        self.client = client
        self.endpoint = endpoint
        self.url = f'{self.client.url}/{self.endpoint}'

        self._config = None

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, data: dict):
        """
        Set config property
        """
        self._config = data

    def _make_path(self, target_path: str):
        """
        Construct a path to the endpoint
        """
        if not target_path:
            return self.url
        return f'{self.url}/{target_path}'

    def get(self, target_path: str = "", endpoint_params: dict = {}):
        """
        Get object configuration on a specific path
        :param target_path: a path to the configuration part
            relative to the endpoint
        :param endpoint_params: any params accepted by the endpoint

        >>> api.interface.get('lo')
        {'ifindex': 1, 'ip': {'address': {'127.0.0.1/8': {}, '::1/128': {}}},
        'link': {'mac': '00:00:00:00:00:00', 'mtu': 65536, ...}
        >>> api.interface.get('lo/ip/address')
        {'127.0.0.1/8': {}, '::1/128': {}}
        >>> api.bridge.get('domain/br_default')
        ...
        """
        url = self._make_path(target_path)

        params = endpoint_params

        request: dict = Request(
            url=url,
            http_session=self.client.http_session,
        ).get(params=params)

        self.config = request

        return self.config

    def patch(self,
              rev: str,
              data: dict,
              target_path: str = "",
              endpoint_params: dict = {}):
        """
        Patch the config on the given endpoint
        :param rev: the branch on which to update configuration
        :param data: the payload to send to the endpoint
        :param target_path: a path to the configuration part
            relative to the endpoint
        :param endpoint_params: any params accepted by the endpoint

        >>> api.revision.create()
        {'1': {'state': 'pending',
               'transition': {'issue': {}, 'progress': ''}}}
        >>> api.interface.patch(rev=api.revision.rev,
                                data=data,
                                target_path="lo/ip")
        {'address': {'10.10.10.4/32': {}}}
        >>> api.revision.apply()
        {'state': 'apply', 'transition': {'issue': {}, 'progress': ''}}
        >>> api.revision.is_applied()
        True
        """
        url = self._make_path(target_path)
        params = endpoint_params
        params['rev'] = rev

        request = Request(
            url=url,
            http_session=self.client.http_session
        ).patch(data, params=params)

        return request

    def post(self, target_path: str = "", endpoint_params: dict = {}):
        """
        Make a POST request on the model
        :param target_path: a path to the configuration part
            relative to the endpoint
        :param endpoint_params: any params accepted by the endpoint
        """
        url = self._make_path(target_path)
        params = endpoint_params
        return Request(
            url=url,
            http_session=self.client.http_session
        ).post(params=params)

    def delete(self,
               rev: str,
               target_path: str = "",
               endpoint_params: dict = {}):
        """
        Delete all configuration for the model on the given path
        :param rev: the branch on which to update configuration
        :param target_path: a path to the configuration part
            relative to the endpoint
        :param endpoint_params: any params accepted by the endpoint

        >>> api.revision.create()
        >>> api.interface.delete(rev=api.revision.rev, target_path='bond21')
        {}
        >>> api.revision.apply()
        {'state': 'apply', 'transition': {'issue': {}, 'progress': ''}}
        >>> api.revision.is_applied()
        True
        """
        url = self._make_path(target_path)
        params = endpoint_params
        params['rev'] = rev

        return Request(
            url=url,
            http_session=self.client.http_session
        ).delete(params=params)


class Revision(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)
        self.rev = None

    def create(self) -> str:
        """
        Create a revision
        """
        request = Request(
            url=self.url,
            http_session=self.client.http_session
        ).post()

        # revision name is set only key of the dictionary
        self.rev = next(iter(request))

        self.config = request

        return self.config

    def apply(self):
        """
        Apply changes in the revision
        """
        if not self.rev:
            raise Exception("No revision to apply")

        url = f'{self.url}/{url_safe(self.rev)}'
        apply_payload = {"state": "apply",
                         "auto-prompt": {"ays": "ays_yes"}}

        request = Request(
            url=url,
            http_session=self.client.http_session
        ).patch(data=apply_payload)

        return request

    def is_applied(self, retries: int = 5, sleep_time: int = 1) -> bool:
        """
        Watch if the status of the revision is applied
        :param retries: the number of checks to perform
        :param sleep_time: the number of seconds to sleep between each retry
        """
        if not self.rev:
            raise Exception("No revision to refresh")

        while retries > 0:
            revision = self.refresh()

            if revision["state"] == 'applied':
                return True

            retries -= 1
            time.sleep(sleep_time)

        return False

    def refresh(self):
        """
        Update the revision properties in-place
        """
        if not self.rev:
            raise Exception("No revision to refresh")

        return self.get(self.rev)

    def switch(self, rev: str):
        """
        Switch to the other revision
        :param rev: the name of the revision
        """
        revision = self.get(rev)
        self.rev = rev
        return revision


class Root(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)

    def diff(self,
             revision_a,
             revision_b: str = "applied",
             endpoint_params: dict = {}):
        """
        Get a diff between 2 revisions.
        `revision_a` will normally be the pending revision you want to apply,
        while `revision_b` is your currently applied revision or
        another pending revision.
        The diff itself is a simple dictionary where removed fields
        have the `null` value.
        :param revision_a: First revision used to get the diff.
        :param revision_b: Second revision used to get the diff.
            Defaults to `applied`.
        :param endpoint_params: additional params accepted by the endpoint.

        Here is an example on how to get the diff between a pending revision
        and currently applied revision:
        >>> api.diff(revision_a="1")
        >>> api.diff(revision_a="2", revision_b="1")
        """
        params = {
            "rev": revision_a,
            "diff": revision_b,
            "filled": False
        }
        params.update(endpoint_params)

        return self.get(endpoint_params=params)


class Router(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)


class Platform(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)


class Bridge(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)


class Mlag(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)


class Evpn(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)


class Qos(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)


class Interface(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)


class Service(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)


class System(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)


class Vrf(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)


class Nve(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)


class Acl(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)


class AAA(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)


class User(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)


class Role(BaseModel):

    def __init__(self, client, endpoint: str) -> None:
        super().__init__(client, endpoint)
