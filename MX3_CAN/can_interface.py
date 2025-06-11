import can
import subprocess
from config import BITRATE

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

    def bring_up(self):
        """
        Activate the CAN interface with the specified bitrate.

        Returns
        -------
        can.Bus
            The CAN bus object associated with the interface.
        """
        try:
            subprocess.run(
                ["sudo", "ip", "link", "set", self.channel, "down"], check=False
            )
            subprocess.run(
                ["sudo", "ip", "link", "set", self.channel, "up", "type", "can", "bitrate", str(self.bitrate)],
                check=True
            )
            self.bus = can.Bus(interface='socketcan', channel=self.channel, bitrate=self.bitrate)
            return self.bus
        except subprocess.CalledProcessError as error:
            raise RuntimeError(f"Failed to activate CAN interface '{self.channel}'") from error

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
