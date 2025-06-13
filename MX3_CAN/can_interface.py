import can
import subprocess
from MX3_CAN.config_yaml import BITRATE

class CANInterface:
    def __init__(self, channel='can0', bitrate=BITRATE):
        """
        Initialize a CANInterface object with a specified channel and bitrate.

        Parameters
        ----------
        channel : str, optional
            The CAN channel to use for communication (default is 'can0').
        bitrate : int, optional
            The bitrate to set for the CAN interface (default is specified by BITRATE).
        """
        self.channel = channel
        self.bitrate = bitrate
        self.bus = None

    def bring_up(self) -> can.BusABC:
        """
        Activate the CAN interface with the specified bitrate.

        This method brings up the CAN interface by executing a system
        command to set the bitrate. It then creates a CAN bus object
        associated with the interface and returns it.

        Returns
        -------
        can.Bus
            The CAN bus object associated with the interface.
        """
        # Bring down the CAN interface
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

        # Bring up the CAN interface with the specified bitrate
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
            raise RuntimeError(
                f"Failed to set bitrate for CAN interface '{self.channel}': {error.stderr}"
            ) from error

        # Create and return the CAN bus object
        self._bus = can.Bus(
            interface="socketcan", channel=self.channel, bitrate=self.bitrate
        )
        return self._bus

    def shutdown(self) -> None:
        """
        Shut down the CAN interface and clean up resources.

        This method deactivates the CAN interface by shutting down the
        associated CAN bus object and executing a system command to bring
        down the network interface. It ensures the CAN interface is properly
        deactivated.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if self.bus:
            self.bus.shutdown()
            self.bus = None
        subprocess.run(["sudo", "ip", "link", "set", self.channel, "down"], check=True)
