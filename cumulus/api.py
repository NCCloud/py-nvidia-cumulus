from requests import Session
from .base import Request
from .models import (Revision, Root,
                     Router, Platform, Bridge,
                     Mlag, Evpn, Qos,
                     Interface, Service, System,
                     Vrf, Nve, Acl, AAA,
                     User, Role)


class Cumulus:
    """
    A thin wrapper around Cumulus API endpoints
    :param str url: a URL to the Cumulus host
        in the format <protocol>://<host>:<port>
    :param tuple auth: Cumulus host authentication details
        in the format ('user', 'pass')

    >>> api = Cumulus(url="http://127.0.0.1:8765",
                      auth=("user", "password"))
    """

    def __init__(self, url: str, auth: tuple, http_session=Session()) -> None:
        self.url = self._format_url(url)
        self.http_session = http_session
        self.http_session.auth = auth

        self.revision = Revision(self, "revision")
        self.root = Root(self, "")
        self.router = Router(self, "router")
        self.platform = Platform(self, "platform")
        self.bridge = Bridge(self, "bridge")
        self.mlag = Mlag(self, "mlag")
        self.evpn = Evpn(self, 'evpn')
        self.qos = Qos(self, "qos")
        self.interface = Interface(self, "interface")
        self.service = Service(self, "service")
        self.system = System(self, "system")
        self.vrf = Vrf(self, "vrf")
        self.nve = Nve(self, "nve")
        self.acl = Acl(self, "acl")
        self.aaa = AAA(self, "system/aaa")
        self.user = User(self, "system/aaa/user")
        self.role = Role(self, "system/aaa/role")

    @staticmethod
    def _format_url(url):
        """
        Set the provided URL in the correct format
        """
        return "{}/nvue_v1".format(url if url[-1] != "/" else url[-1])

    def health(self):
        """
        Verify connection to the Cumulus host
        >>> api.health()
        {'build': 'Cumulus Linux 5.3.0',
        'hostname': 'leaf01',
        'timezone': 'Etc/UTC',
        'uptime': 175827}
        """
        return Request(
            url=f'{self.url}/system',
            http_session=self.http_session
        ).get()
