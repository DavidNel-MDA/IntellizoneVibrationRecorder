import smbus2

class LSM9DS1Device:
    """
    Class to interact with the LSM9DS1 IMU sensor over I2C
    """

    def __init__(self, i2c_bus: int, accel_gyro_address: int, magnetometer_address: int):
        """
        Parameters
        ----------
        i2c_bus : int
            The I2C bus number
        accel_gyro_address : int
            The I2C address of the accelerometer and gyroscope
        magnetometer_address : int
            The I2C address of the magnetometer
        """
        self.bus = smbus2.SMBus(i2c_bus)
        self.addr_ag = accel_gyro_address
        self.addr_mag = magnetometer_address

    def _get_address(self, addr_type: str) -> int:
        """
        Get the address of the LSM9DS1 device based on the addr_type parameter.

        Parameters:
            addr_type (str): The type of the address to retrieve. Valid values are 'AG' (accelerometer and gyroscope) and 'MAG' (magnetometer)

        Returns:
            int: The address of the device

        Raises:
            ValueError: If an invalid addr_type is provided
        """
        # Check if the addr_type parameter is valid
        if addr_type.upper() == "AG":
            # Return the address of the accelerometer and gyroscope
            return self.addr_ag
        elif addr_type.upper() == "MAG":
            # Return the address of the magnetometer
            return self.addr_mag
        # Raise an error if an invalid addr_type is provided
        raise ValueError(f"Invalid addr_type '{addr_type}' (use 'AG' or 'MAG')")

    def write_byte(self, addr_type: str, reg: int, value: int) -> None:
        """
        Write a byte to a register on the LSM9DS1 device.

        Parameters
        ----------
        addr_type : str
            The type of the address to write to. Valid values are 'AG' (accelerometer and gyroscope) and 'MAG' (magnetometer)
        reg : int
            The register to write to
        value : int
            The value to write to the register

        Returns
        -------
        None
        """
        addr = self._get_address(addr_type)
        self.bus.write_byte_data(addr, reg, value)

    def read_bytes(self, addr_type: str, start_reg: int, length: int) -> list[int]:
        """
        Read a multiple bytes from the LSM9DS1 device.

        Parameters
        ----------
        addr_type : str
            The type of the address to read from. Valid values are 'AG' (accelerometer and gyroscope) and 'MAG' (magnetometer)
        start_reg : int
            The starting register to read from
        length : int
            The number of bytes to read

        Returns
        -------
        list[int]
            A list of the bytes read from the device
        """
        addr = self._get_address(addr_type)
        return self.bus.read_i2c_block_data(addr, start_reg, length)

    def read_byte(self, addr_type: str, reg: int) -> int:
        """
        Read a single byte from the LSM9DS1 device.

        Parameters
        ----------
        addr_type : str
            The type of the address to read from. Valid values are 'AG' (accelerometer and gyroscope) and 'MAG' (magnetometer)
        reg : int
            The register to read from

        Returns
        -------
        int
            The byte read from the device
        """
        addr = self._get_address(addr_type)
        return self.bus.read_byte_data(addr, reg)

    def read_word(self, addr_type: str, reg: int, signed: bool = True) -> int:
        """
        Read a word (2 bytes) from the LSM9DS1 device starting at the specified register.

        Parameters
        ----------
        addr_type : str
            The type of the address to read from. Valid values are 'AG' (accelerometer and gyroscope) and 'MAG' (magnetometer).
        reg : int
            The starting register to read the word from.
        signed : bool, optional
            Whether the word should be interpreted as a signed integer (default is True).

        Returns
        -------
        int
            The word read from the device, interpreted according to the 'signed' parameter.
        """
        # Read 2 bytes from the specified register
        raw = self.read_bytes(addr_type, reg, 2)
        # Convert the raw bytes to an integer with the specified byte order and signedness
        return int.from_bytes(raw, byteorder="little", signed=signed)

    def update_bits(self, addr_type: str, reg: int, mask: int, value: int):
        """
        Update the specified bits in a register on the LSM9DS1 device.

        Parameters
        ----------
        addr_type : str
            The type of the address to write to. Valid values are 'AG' (accelerometer and gyroscope) and 'MAG' (magnetometer).
        reg : int
            The register to write to.
        mask : int
            A mask of the bits to update. The bits in the mask will be replaced with the specified value.
        value : int
            The new value to write to the register.

        Returns
        -------
        None
        """
        current = self.read_byte(addr_type, reg)
        new_val = (current & ~mask) | (value & mask)
        self.write_byte(addr_type, reg, new_val)
