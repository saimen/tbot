import abc
import typing
import pathlib
import paramiko
from tbot.machine import channel
from tbot.machine.linux import auth
from .machine import LabHost

SLH = typing.TypeVar("SLH", bound="SSHLabHost")


class SSHLabHost(LabHost):

    @property
    @abc.abstractmethod
    def hostname(self) -> str:
        """Return the hostname of this lab."""
        pass

    @property
    def authenticator(self) -> auth.Authenticator:
        """Return an authenticator that allows logging in on the labhost."""
        return auth.PrivateKeyAuthenticator(pathlib.Path.home() / ".ssh" / "id_rsa")

    @property
    def port(self) -> int:
        """Return the port the SSH server is listening on."""
        return 22

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} {self.username}@{self.hostname}:{self.port}>"
        )

    def __init__(self) -> None:
        super().__init__()
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()

        password = None
        key_file = None

        authenticator = self.authenticator
        if isinstance(authenticator, auth.PasswordAuthenticator):
            password = authenticator.password
        if isinstance(authenticator, auth.PrivateKeyAuthenticator):
            key_file = str(authenticator.key)

        self.client.connect(
            self.hostname, port=self.port, password=password, key_filename=key_file
        )

        self.channel = channel.ParamikoChannel(
            self.client.get_transport().open_session()
        )

    def destroy(self) -> None:
        self.client.close()

    def _obtain_channel(self) -> channel.Channel:
        return self.channel

    def _new_channel(self) -> channel.Channel:
        return channel.ParamikoChannel(self.client.get_transport().open_session())