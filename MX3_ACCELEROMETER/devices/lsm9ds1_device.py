import smbus2


class LSM9DS1Device:
    def __init__(
        self, i2c_bus: int, accel_gyro_address: int, magnetometer_address: int
    ):
        """
        Initialize the LSM9DS1 device with the specified I2C bus and addresses.

        Parameters
        ----------
        i2c_bus : int
            The I2C bus number to use for communication.
        accel_gyro_address : int
            The I2C address for the accelerometer and gyroscope.
        magnetometer_address : int
            The I2C address for the magnetometer.
        """
        # Initialize the I2C bus
        self.bus = smbus2.SMBus(i2c_bus)

        # Store the I2C addresses for the accelerometer/gyroscope and magnetometer
        self.addr_ag = accel_gyro_address
        self.addr_mag = magnetometer_address

    def _get_address(self, addr_type: str) -> int:
        """
        Internal: Resolve 'AG' or 'MAG' into the corresponding I2C address.

        Parameters
        ----------
        addr_type : str
            The type of address to resolve. Valid values are 'AG' for the
            accelerometer and gyroscope, and 'MAG' for the magnetometer.

        Returns
        -------
        int
            The I2C address for the specified device.

        Raises
        ------
        ValueError
            If the specified addr_type is not valid.
        """
        addr_type = addr_type.upper()
        if addr_type == "AG":
            return self.addr_ag
        elif addr_type == "MAG":
            return self.addr_mag
        raise ValueError(f"Invalid addr_type '{addr_type}'. Use 'AG' or 'MAG'.")

    def write_byte(self, addr_type: str, reg: int, value: int) -> None:
        """
        Write a single byte to a register.

        Parameters
        ----------
        addr_type : str
            The type of address to write to. Valid values are 'AG' for the
            accelerometer and gyroscope, and 'MAG' for the magnetometer.
        reg : int
            The register to write to.
        value : int
            The value to write.
        """
        addr = self._get_address(addr_type)
        self.bus.write_byte_data(addr, reg, value)

    def read_byte(self, addr_type: str, reg: int) -> int:
        """
        Read a single byte from a register.

        Parameters
        ----------
        addr_type : str
            The type of address to read from. Valid values are 'AG' for the
            accelerometer and gyroscope, and 'MAG' for the magnetometer.
        reg : int
            The register to read from.

        Returns
        -------
        int
            The value read from the register.
        """
        addr = self._get_address(addr_type)
        return self.bus.read_byte_data(addr, reg)

    def read_bytes(self, addr_type: str, start_reg: int, length: int) -> list[int]:
        """
        Read multiple consecutive bytes from a device starting at a given register.

        Parameters
        ----------
        addr_type : str
            The type of address to read from. Valid values are 'AG' for the
            accelerometer and gyroscope, and 'MAG' for the magnetometer.
        start_reg : int
            The register to start reading from.
        length : int
            The number of bytes to read.

        Returns
        -------
        list[int]
            A list of the read bytes.
        """
        addr = self._get_address(addr_type)
        return self.bus.read_i2c_block_data(addr, start_reg, length)

    def read_word(self, addr_type: str, reg: int, signed: bool = True) -> int:
        """
        Read a 16-bit value from two consecutive registers (little-endian).

        Parameters
        ----------
        addr_type : str
            The type of address to read from. Valid values are 'AG' for the
            accelerometer and gyroscope, and 'MAG' for the magnetometer.
        reg : int
            The register address of the low byte of the value to read.
        signed : bool, optional
            Whether to interpret the value as signed. Defaults to True.

        Returns
        -------
        int
            The read 16-bit value.
        """
        # Read two consecutive bytes from the device
        raw = self.read_bytes(addr_type, reg, 2)

        # Interpret the bytes as a 16-bit little-endian value
        value = int.from_bytes(raw, byteorder="little", signed=signed)

        # Return the read value
        return value

    def write_bits(self, addr_type: str, reg: int, mask: int, value: int):
        """
        Update specific bits in a register using a bit-masked write.

        This is a convenience function that allows you to set specific
        bits in a register without having to read the current value,
        modify it, and then write it back. It does all of that internally.

        Parameters
        ----------
        addr_type : str
            The type of address to write to. Valid values are 'AG' for the
            accelerometer and gyroscope, and 'MAG' for the magnetometer.
        reg : int
            The register address to write to.
        mask : int
            A bitmask of the bits to update in the register.
        value : int
            The new value of the bits that are being updated. This value
            should already be aligned to the mask so that the correct bits
            are set.
        """
        current = self.read_byte(addr_type, reg)
        # Clear the bits that are going to be updated
        new_val = current & ~mask
        # Set the bits that are being updated
        new_val |= value & mask
        # Write the new value back to the register
        self.write_byte(addr_type, reg, new_val)

    def set_bit(self, addr_type: str, reg: int, bit_position: int):
        """
        Set a single bit in a register.

        This method sets the bit at the specified position in the
        register to 1. The bit is set using a bit-wise OR operation
        with the current value of the register and a mask where the
        bit is set to 1 and all other bits are set to 0.

        Parameters
        ----------
        addr_type : str
            The type of address to write to. Valid values are 'AG' for the
            accelerometer and gyroscope, and 'MAG' for the magnetometer.
        reg : int
            The register address to write to.
        bit_position : int
            The position of the bit to set in the register.
        """
        current = self.read_byte(addr_type, reg)
        self.write_byte(addr_type, reg, current | (1 << bit_position))

    def clear_bit(self, addr_type: str, reg: int, bit_position: int):
        """
        Clear a single bit in a register.

        This method clears the bit at the specified position in the
        register by setting it to 0. The bit is cleared using a bit-wise
        AND operation with the current value of the register and a mask
        where the bit is set to 0 and all other bits are set to 1.

        Parameters
        ----------
        addr_type : str
            The type of address to write to. Valid values are 'AG' for the
            accelerometer and gyroscope, and 'MAG' for the magnetometer.
        reg : int
            The register address to write to.
        bit_position : int
            The position of the bit to clear in the register.
        """
        current = self.read_byte(addr_type, reg)
        self.write_byte(addr_type, reg, current & ~(1 << bit_position))
