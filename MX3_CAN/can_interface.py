import subprocess

import can

from MX3_CAN.config_yaml import BITRATE


class CANInterface:
    """
    A class for creating a CAN bus interface on a Raspberry Pi.

    Args:
        channel (str): The name of the CAN bus interface (e.g. 'can0').
        bitrate (int): The bitrate of the CAN bus (e.g. 500000).

    Attributes:
        channel (str): The name of the CAN bus interface.
        bitrate (int): The bitrate of the CAN bus.
        bus (can.BusABC): The CAN bus interface.
    """

    def __init__(self, channel="can0", bitrate=BITRATE):
        """
        Initialize a CAN bus interface.

        Args:
            channel (str): The name of the CAN bus interface.
            bitrate (int): The bitrate of the CAN bus.

        Returns:
            None
        """
        self.channel = channel
        self.bitrate = bitrate
        self.bus = None

    def bring_up(self) -> can.BusABC:
        """
        Bring up the CAN bus interface with the specified bitrate and create a
        CAN bus object.

        Returns:
            can.BusABC: The CAN bus object.
        """
        # Bring down the CAN interface
        self._bring_interface_down()

        # Bring up the CAN interface with the specified bitrate
        self._set_bitrate()

        # Create and return the CAN bus object
        self.bus = can.Bus(
            interface="socketcan", channel=self.channel, bitrate=self.bitrate
        )
        return self.bus

    def _bring_interface_down(self) -> None:
        """Bring down the CAN interface.

        This method is a no-op if the interface is already down. If the interface
        is not down, it will be brought down using the `ip link set` command.

        Raises:
            RuntimeError: If the command fails to bring down the interface.
        """
        # Attempt to bring down the CAN interface
        try:
            subprocess.run(
                ["sudo", "ip", "link", "set", self.channel, "down"],
                check=False,
                capture_output=True,
            )
        except subprocess.CalledProcessError as error:
            raise RuntimeError(
                f"Failed to bring down CAN interface '{self.channel}': {error.stderr}"
            ) from error

    def _set_bitrate(self) -> None:
        """
        Set the bitrate for the CAN interface.

        This method configures the CAN interface with the specified bitrate
        using the `ip link set` command. It brings up the interface if it's
        not already up.

        Raises:
            RuntimeError: If the command fails to set the bitrate.
        """
        # Attempt to bring up the CAN interface with the specified bitrate
        try:
            subprocess.run(
                [
                    "sudo",
                    "ip",
                    "link",
                    "set",
                    self.channel,
                    "up",
                    "type",
                    "can",
                    "bitrate",
                    str(self.bitrate),
                ],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as error:
            # Raise a runtime error if setting the bitrate fails
            raise RuntimeError(
                f"Failed to set bitrate for CAN interface '{self.channel}': {error.stderr}"
            ) from error

    def shutdown(self) -> None:
        """
        Shut down the CAN bus interface.

        This method brings down the CAN interface and releases any system resources
        associated with it. It also shuts down the CAN bus object.
        """
        if self.bus:
            # Shut down the CAN bus object
            self.bus.shutdown()
            self.bus = None

        # Bring down the CAN interface
        subprocess.run(
            ["sudo", "ip", "link", "set", self.channel, "down"],
            check=True,
        )
