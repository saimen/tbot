# TBot, Embedded Automation Tool
# Copyright (C) 2018  Harald Seiler
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import abc
import contextlib
import time
import typing
import tbot
from tbot.machine import linux
from tbot.machine import channel

Self = typing.TypeVar("Self", bound="Board")


class Board(contextlib.AbstractContextManager):
    """
    Abstract base class for boards.

    **Implementation example**::

        from tbot.machine import board
        from tbot.machine import channel
        from tbot.machine import linux

        class MyBoard(board.Board):
            name = "my-board"

            def poweron(self) -> None:
                # Command to power on the board
                self.lh.exec0("poweron", self.name)

            def poweroff(self) -> None:
                # Command to power off the board
                self.lh.exec0("poweroff", self.name)

            def connect(self) -> channel.Channel:
                return self.lh.new_channel(
                    "picocom",
                    "-b",
                    "115200",
                    linux.Path(self.lh, "/dev") / f"tty-{self.name}",
                )
    """

    @property
    def connect_wait(self) -> typing.Optional[float]:
        """
        Time to wait after connecting before powering on (:class:`float`).

        This is supposed to allow telnet/rlogin/whatever to take some time
        to establish the connection.
        """
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name of this board."""
        pass

    def console_check(self) -> None:
        """
        Run this check before actually interacting with the board.

        This hook allows you to ensure the console is unoccupied so you
        don't accidentally interfere with other developers.

        Return if the console if ok, raise an Exception if it is not.

        .. note::
            If the connect command fails in less than ``connect_wait``
            seconds, this check is not needed.  It is, however, definitely
            the safer way.
        """
        pass

    @abc.abstractmethod
    def poweron(self) -> None:
        """Power on this board."""
        pass

    @abc.abstractmethod
    def poweroff(self) -> None:
        """Power off this board."""
        pass

    def connect(self) -> typing.Optional[channel.Channel]:
        """Connect to the serial port of this board."""
        return None

    def cleanup(self) -> None:
        """
        Cleanup the connection.

        Might be necessary if the TBot's default behaviour
        of just killing the shell leaves lock files behind.
        """
        pass

    def __init__(self, lh: linux.LabHost) -> None:
        """
        Initialize an instance of this board.

        This will not yet power on the board. For that you need to use a ``with``
        block::

            with MyBoard(lh) as b:
                ...

        :param tbot.machine.linux.LabHost lh: LabHost from where to connect to the Board.
        """
        self.lh = lh
        self.channel = self.connect()
        if self.connect_wait is not None:
            time.sleep(self.connect_wait)
        if self.channel is not None and not self.channel.isopen():
            raise RuntimeError("Could not connect to board!")
        self._rc = 0

        if self.channel is not None:

            def cleaner(_: channel.Channel) -> None:
                self.cleanup()

            self.channel.register_cleanup(cleaner)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.lh!r})"

    def __enter__(self: Self) -> Self:
        self._rc += 1
        if self._rc > 1:
            return self
        self.console_check()
        tbot.log.EventIO(
            ["board", "on", self.name],
            tbot.log.c("POWERON").bold + f" ({self.name})",
            verbosity=tbot.log.Verbosity.QUIET,
        )
        self.poweron()
        self.on = True
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        self._rc -= 1
        if self._rc == 0:
            tbot.log.EventIO(
                ["board", "off", self.name],
                tbot.log.c("POWEROFF").bold + f" ({self.name})",
                verbosity=tbot.log.Verbosity.QUIET,
            )
            self.poweroff()
